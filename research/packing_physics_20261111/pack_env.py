"""PACK-EVID original 5x7 OSC physical environment, no upper API imports.

Constructor truth and measured scoring state stay outside public observations.
No state/pose assignment is performed after reset. Work stage transitions use
measured rigid bodies, real support/contact, settling and actual lid joints.
"""
import copy,hashlib,json,pathlib,re,sys
import numpy as np
from geometry import inject,SURFACE,ITEM_STARTS,LAYOUTS,SIZES,HEIGHTS,COLORS,BATCH_COLORS,LETTERS,KINDS
E=pathlib.Path('/root/autodl-tmp/experiments/three-skill-crossbench-pilot-20261021-apiyi-v1')
R=E/'Long-context-continuity-study-20261107-v1';B=R/'benchmarks/pinned/robomemarena/evaluation_benchmark'
sys.path[:0]=[str(R),str(B/'scripts')]

def make_native(carrier,root):
    from robomemarena_entry import install_native_package_alias
    install_native_package_alias(B)
    import libero.libero.envs.env_wrapper as wrapper
    base=wrapper.TASK_MAPPING['libero_coffee_table_manipulation']
    class Pack_Evidence_Manipulation(base):
        def _load_model(self):
            super()._load_model();self.pack_objects,self.pack_fixtures,self.pack_pads=inject(self.model,carrier)
        def _check_success(self):return False # this extension owns a separate custom score
    wrapper.TASK_MAPPING['pack_evidence_manipulation']=Pack_Evidence_Manipulation
    wrapper.TASK_MAPPING['Pack_Evidence_Manipulation']=Pack_Evidence_Manipulation
    import libero.libero.envs.regions as regions
    for name in regions.get_region_samplers.__code__.co_names:
        registry=getattr(regions,name,None)
        if isinstance(registry,dict) and 'libero_coffee_table_manipulation' in registry:registry['pack_evidence_manipulation']=registry['libero_coffee_table_manipulation']
    import eval_common as ec
    text=ec._resolve_bddl_path(1).read_text();text=re.sub(r'(\(problem\s+)[^\s)]+',r'\1pack_evidence_manipulation',text,count=1)
    root=pathlib.Path(root);root.mkdir(parents=True,exist_ok=True);path=root/'scene.bddl';path.write_text(text)
    return wrapper.OffScreenRenderEnv(bddl_file_name=str(path),camera_heights=256,camera_widths=256,
        ignore_done=True,reward_shaping=False,control_freq=20,initialization_noise=None,hard_reset=False)

class PackPhysicalEnv:
    def __init__(self,carrier,root):
        self.root=pathlib.Path(root);self.carrier=carrier;self.native=make_native(carrier,self.root)
        self.sim=self.native.sim;self.objects=self.native.env.pack_objects;self.boxes=self.native.env.pack_fixtures;self.pads=self.native.env.pack_pads
        self.closed=False;self.max_steps=2500;self.max_decisions=600
        self.family_by_id={r['case_id']:r['family'] for r in json.loads((pathlib.Path(__file__).parent/'release/cases.json').read_text())}
        self.station_defaults={gid:np.asarray(self.sim.model.geom_pos[gid]).copy() for gid in range(self.sim.model.ngeom) if (self.sim.model.geom_id2name(gid) or '').startswith('pack_station_')}
        self.sim.forward()
        # HOPE attachment sites are not exact visible mesh bounds. Put labels
        # outside the actual rendered mesh rather than burying glyphs in it.
        for item,info in self.objects.items():
            root=self.sim.model.body_name2id(info['body']);body_pos=np.asarray(self.sim.data.get_body_xpos(info['body']));body_rot=np.asarray(self.sim.data.get_body_xmat(info['body'])).reshape(3,3)
            zs=[]
            for gid,bid in enumerate(self.sim.model.geom_bodyid):
                name=self.sim.model.geom_id2name(gid) or ''
                if int(bid)!=root or int(self.sim.model.geom_type[gid])!=7:continue
                mesh=int(self.sim.model.geom_dataid[gid]);start=int(self.sim.model.mesh_vertadr[mesh]);count=int(self.sim.model.mesh_vertnum[mesh]);vertices=np.asarray(self.sim.model.mesh_vert[start:start+count])
                rot=np.asarray(self.sim.data.geom_xmat[gid]).reshape(3,3);pos=np.asarray(self.sim.data.geom_xpos[gid]);local=((vertices@rot.T+pos)-body_pos)@body_rot
                zs.extend([float(local[:,2].min()),float(local[:,2].max())])
            info['visual_bottom']=min(zs) if zs else info['bottom'];info['visual_top']=max(zs) if zs else info['top']
    def reset(self,public,private,initial_state=None):
        self.public=copy.deepcopy(public);self.private=copy.deepcopy(private);self.truth=self.private['truth']
        self.task_family=self.family_by_id[self.public['episode_ref']]
        self.steps=0;self.act_chunks=0;self.stage=0;self.stable=0;self.relay_stage=0;self.relay_count=0;self.last_stage_step=0
        self.events=[];self.expected_bindings={};self.handed=False;self.terminal=False;self.success=None;self.reason=None;self.reopens=0
        self.query=None;self._score_cache=None;self._frames={};self.obs_index=0;self.last_public_ref=None;self.previous_lids=[False,False];self.was_closed=[False,False]
        self.native.env.robots[0].gripper.current_action[:]=0
        seed=int(hashlib.sha256(self.public['episode_ref'].encode()).hexdigest()[:8],16)%(2**31-1)
        # Paired conditions must not change native RNG. Episode IDs differ by
        # condition, so seed only from public-independent constructor truth.
        seed=int(hashlib.sha256(json.dumps(self.truth,sort_keys=True).encode()).hexdigest()[:8],16)%(2**31-1)
        self.native.seed(seed);self.native.reset()
        for i,obj in enumerate(self.native.env.objects_dict.values()):
            if obj.joints:self.sim.data.set_joint_qpos(obj.joints[0],np.array([2+i*.15,2,.1,1,0,0,0]))
        offset=np.asarray(self.truth['layout_offset']);perm=self.truth['public_permutation']
        for gid,original in self.station_defaults.items():self.sim.model.geom_pos[gid]=original+np.r_[offset,0.]
        self.starts={};self.box_starts={}
        for i,(item,info) in enumerate(self.objects.items()):
            start=np.asarray(ITEM_STARTS[perm[i]],float).copy();start[:2]+=offset;start[2]=SURFACE-info['bottom']+.012
            self.sim.data.set_joint_qpos(info['joint'],np.r_[start,[1.,0.,0.,0.]])
            self.starts[item]=start
            mark=self.sim.model.body_name2id('pack_'+item+'_mark_tag');lot=self.sim.model.body_name2id('pack_'+item+'_lot_tag')
            self.sim.model.body_pos[mark]=[.035,0,info['visual_top']+.0025 if self.private['initial_cue'] else info['visual_bottom']-.0025]
            self.sim.model.body_quat[mark]=[1,0,0,0] if self.private['initial_cue'] else [0,1,0,0]
            self.sim.model.body_pos[lot]=[-.035,0,info['visual_bottom']-.0025];self.sim.model.body_quat[lot]=[0,1,0,0]
            self.sim.model.geom_rgba[self.sim.model.geom_name2id('pack_'+item+'_lot_base')]=BATCH_COLORS[self.truth['items'][item]['lot']]
            self.sim.model.geom_rgba[self.sim.model.geom_name2id('pack_'+item+'_mark')]=COLORS[self.truth['items'][item]['mark']]
            for segment in 'abcdefg':
                color=(.02,.02,.02,1) if segment in LETTERS[self.truth['items'][item]['lot']] else (.95,.95,.95,1)
                self.sim.model.geom_rgba[self.sim.model.geom_name2id('pack_'+item+'_lot_'+segment)]=color
        for i,(name,info) in enumerate(self.boxes.items()):
            start=np.asarray(LAYOUTS[self.carrier][i],float).copy();start[:2]+=offset;start[2]=SURFACE+.009
            self.box_starts[name]=start;self.sim.data.set_joint_qpos(info['joint'],np.r_[start,[1.,0.,0.,0.]])
            self.sim.data.set_joint_qpos(info['lid_joint'],.24)
        self.sim.data.qvel[:]=0;self.sim.data.qacc_warmstart[:]=0;self.sim.data.qfrc_applied[:]=0;self.sim.data.xfrc_applied[:]=0;self.sim.forward()
        for _ in range(10):self.native.step([0,0,0,0,0,0,-1.])
        if initial_state is not None:self.sim.set_state_from_flattened(np.asarray(initial_state))
        self.sim.forward();self.native.env._update_observables(force=True);self._obs=self.native.env._get_observations()
        self.initial_state_sha=hashlib.sha256(self.sim.get_state().flatten().tobytes()).hexdigest()
        self.commands=list(self.public['workflow']);self.initial_positions={k:self.position(k) for k in self.objects|self.boxes}
        return self.observation()
    def position(self,name):
        info=(self.objects|self.boxes)[name];return np.asarray(self.sim.data.get_body_xpos(info['body'])).copy()
    def lid_q(self,name):return float(self.sim.data.get_joint_qpos(self.boxes[name]['lid_joint']))
    def _body_ids(self,root):
        parent=np.asarray(self.sim.model.body_parentid);ids={int(self.sim.model.body_name2id(root))}
        for _ in range(5):ids|={i for i,p in enumerate(parent) if int(p) in ids}
        return ids
    def _contact(self,item,target):
        a=self._body_ids((self.objects|self.boxes)[item]['body']);b=self._body_ids((self.objects|self.boxes)[target]['body']) if target in self.boxes else {0,int(self.sim.model.body_name2id('coffee_table'))}
        return any((int(self.sim.model.geom_bodyid[c.geom1]) in a and int(self.sim.model.geom_bodyid[c.geom2]) in b) or
            (int(self.sim.model.geom_bodyid[c.geom2]) in a and int(self.sim.model.geom_bodyid[c.geom1]) in b) for c in self.sim.data.contact[:self.sim.data.ncon])
    def _released(self,name):
        info=(self.objects|self.boxes)[name];speed=np.linalg.norm(self.sim.data.get_body_xvelp(info['body']))
        fingers=np.asarray(self._obs['robot0_gripper_qpos'])
        return bool(speed<.15 and np.mean(np.abs(fingers))>.012)
    def inside(self,item,container):
        p=self.position(item);c=self.position(container);sx,sy=self.boxes[container]['size'];h=self.boxes[container]['height']
        rotation=np.asarray(self.sim.data.get_body_xmat(self.boxes[container]['body'])).reshape(3,3);local=rotation.T@(p-c)
        top=max(self.objects[item]['top'],self.objects[item]['visual_top'])
        return bool(abs(local[0])<sx-.008 and abs(local[1])<sy-.008 and -.005<local[2] and local[2]+top<h+.007 and self._released(item) and self._contact(item,container))
    def at(self,name,target):
        p=self.position(name);return bool(np.linalg.norm(p[:2]-np.asarray(target)[:2])<.035 and SURFACE-.01<p[2]<SURFACE+.15 and self._released(name) and self._contact(name,'table'))
    def measured_binding(self,item):
        matches=[c for c in self.boxes if self.inside(item,c)];return matches[0] if len(matches)==1 else None
    def _satisfied(self,command):
        a=command.split(':');kind=a[0]
        if kind in ('p','t'):return self.inside('i'+a[1],'c'+a[2])
        if kind=='x':return self.inside('i0','c'+a[2]) and self.inside('i1','c'+a[1])
        if kind=='close':return abs(self.lid_q('c'+a[1]))<.007
        if kind=='reopen_work':return self.lid_q('c'+a[1])>.20
        if kind=='handover':
            active=set(self.expected_bindings.values())
            return bool(active) and all(self.inside(i,c) for i,c in self.expected_bindings.items()) and all(self.at(c,self.pads['handover'+c[1]]) for c in active)
        if kind=='return':return self.at('c'+a[1],self.box_starts['c'+a[1]])
        if kind=='relay':
            item='i'+a[1];target=self.pads['transit'] if self.relay_stage==0 else self.initial_positions[item]
            if self.at(item,target):
                self.relay_stage+=1
                if self.relay_stage==2:self.relay_stage=0;return True
            return False
        if kind=='wait':return self.steps-self.last_stage_step>=10*int(self.truth['delay_units'])
        raise ValueError('UnsupportedPhysicalCommand:'+kind)
    def _update(self):
        if not hasattr(self,'last_stage_step'):self.last_stage_step=0
        current=self.commands[self.stage] if self.stage<len(self.commands) else ''
        open_lids=[self.lid_q(c)>.04 for c in self.boxes]
        for i,opened in enumerate(open_lids):
            if self.was_closed[i] and opened and not self.previous_lids[i]:
                self.reopens+=1
                legal=current=='reopen_work:'+str(i) or self.private['recoverable']
                self.events.append({'step':self.steps,'kind':'actual_lid_reopened','container':'c'+str(i),'public_rule_legal':legal})
                if not legal:self._finish(False,'public_reinspection_rule_violation')
        self.previous_lids=open_lids
        if self.terminal:return
        if self.stage<len(self.commands):
            satisfied=self._satisfied(current)
            # relay internally spans two placements; its completed signal is
            # already a conjunction of measured state, not three repeated ACKs.
            self.stable=(3 if current.startswith('relay:') else self.stable+1) if satisfied else 0
            if self.stable>=3:
                self.events.append({'step':self.steps,'kind':'measured_work_goal','command':current,'stage':self.stage})
                fields=current.split(':')
                if fields[0] in ('p','t'):self.expected_bindings['i'+fields[1]]='c'+fields[2]
                if fields[0]=='x':
                    left,right='c'+fields[1],'c'+fields[2]
                    self.expected_bindings={i:right if c==left else left if c==right else c for i,c in self.expected_bindings.items()}
                if current.startswith('close:'):self.was_closed[int(current.split(':')[1])]=True
                if current=='handover':self.handed=True
                self.stage+=1;self.stable=0;self.last_stage_step=self.steps
        if self.stage==len(self.commands) and self.query is None:
            item='i'+str(self.truth['query_item'])
            if not self.private['required']:self.query={'item':'dispatch','field':'outside_label'}
            elif self.task_family=='binding':self.query={'container':self.measured_binding(item),'field':self.truth['query_field'],'response':'one value per current item, retaining duplicates'}
            else:self.query={'item':item,'field':self.truth['query_field']}
            self.events.append({'step':self.steps,'kind':'public_workorder_arrived'})
        if self.steps>=self.max_steps:self._finish(False,'original_control_step_budget')
    def _advance(self,action):
        self._obs,_,_,_=self.native.step(np.asarray(action,dtype=float).tolist());self.steps+=1;self._update()
    def step(self,actions):
        if self.terminal:raise RuntimeError('EpisodeAlreadyTerminal')
        a=np.asarray(actions,dtype=np.float32)
        if a.shape!=(5,7) or not np.isfinite(a).all():raise ValueError('Original5x7OSCRequired')
        self.act_chunks+=1
        for action in a:
            self._advance(action)
            if self.terminal:break
        return self.observation(),self.terminal
    def public_task(self):
        names={'i'+str(i):k.replace('_',' ') for i,k in enumerate(KINDS)}
        phrases=[]
        for cmd in self.public['workflow']:
            a=cmd.split(':');kind=a[0]
            if kind in ('p','t'):s=('put ' if kind=='p' else 'repack ')+names['i'+a[1]]+' into container '+a[2]
            elif kind=='close':s='close container '+a[1]
            elif kind=='reopen_work':s='legally reopen container '+a[1]+' for the scheduled repack'
            elif kind=='return':s='return container '+a[1]+' to its marked starting station'
            elif kind=='relay':s='move '+names['i'+a[1]]+' to the cyan transit pad and back to its initial pad'
            elif kind=='x':s='exchange the cream cheese and butter between the two containers, using the transit pad if needed'
            elif kind=='handover':s='move all filled containers to their yellow handover pads'
            else:s='continue the ordinary work'
            phrases.append(s)
        requirement=('A later work order asks about one packed item and its current container; '+('only mark color may be requested.' if self.public.get('possible_late_fields')==['mark'] else 'either mark color or batch letter may be required.')) if self.private['required'] else 'The later work order concerns only the visible outside dispatch label, not the item marks.'
        rule='After a scheduled close/handover, extra reinspection is permitted with the original action budget.' if self.private['recoverable'] else 'After a scheduled close/handover, extra reopening is forbidden except the explicitly scheduled reopen step.'
        text='Public object aliases: i0 cream cheese, i1 butter, i2 cookies. Containers have one/two white bars denoting c0/c1. Item marks are large colors. Underside batch labels use redundant letter and large background color: A yellow, B cyan, C magenta, D orange, E purple, F gray. '+requirement+' '+rule+' Work: '+'; then '.join(phrases)+'.'
        if self.query:text+=' Current public work order: '+json.dumps(self.query)+'. For a container question return a list of contents field values, retaining duplicates; for an item question return its field value. Also submit container and public source refs, or unknown. Outside label is lane_public.'
        if self.last_public_ref:text+=' Current original observation reference: '+self.last_public_ref+'.'
        return text
    def observation(self):
        from policy_adapter import build_eval26_policy_input
        _,main,wrist=build_eval26_policy_input(self._obs,self.public_task(),256)
        self.obs_index+=1;ref='obs-'+str(self.obs_index);self.last_public_ref=ref
        self._frames[ref]={'step':self.steps,'binding':{i:self.measured_binding(i) for i in self.objects}}
        return {'RGB':{'main':main,'wrist':wrist},'proprio':{'eef_position':np.asarray(self._obs['robot0_eef_pos']),
          'eef_quaternion':np.asarray(self._obs['robot0_eef_quat']),'finger_positions':np.asarray(self._obs['robot0_gripper_qpos'])},
          'task_instruction':self.public_task(),'observation_ref':ref,'terminated':self.terminal}
    def submit_verification(self,value,container,evidence_ids):
        if self.terminal:raise RuntimeError('EpisodeAlreadyTerminal')
        if self.query is None:raise ValueError('PublicWorkorderNotYetArrived')
        if len(set(evidence_ids))>8 or not set(evidence_ids)<=set(self._frames):raise ValueError('PublicReferenceBoundary')
        if self.private['required']:
            work_intact=all(self.inside(i,c) for i,c in self.expected_bindings.items())
            if 'container' in self.query:
                selected=self.query['container'];expected=sorted(self.truth['items'][i][self.query['field']].casefold() for i in self.objects if self.inside(i,selected))
                values=value if isinstance(value,list) else re.split(r'[,;\s]+',value.strip()) if isinstance(value,str) else []
                correct=bool(expected) and sorted(str(v).casefold() for v in values)==expected and container==selected and work_intact
            else:
                item=self.query['item'];correct=value==self.truth['items'][item][self.query['field']] and container==self.measured_binding(item) and work_intact
        else:correct=value=='lane_public' and all(self.inside(i,c) for i,c in self.expected_bindings.items())
        self._finish(bool(correct),'submitted_delayed_verification')
        return {'submitted':True,'terminated':True} # no private expected answer
    def _finish(self,success,reason):
        if not self.terminal:self.terminal=True;self.success=bool(success);self.reason=reason
    def scorer_result(self):
        if self._score_cache is None and self.terminal:self._score_cache={'schema':'PACK-EVID-physical-v2','valid':True,'success':self.success,'reason':self.reason,
            'control_steps':self.steps,'act_chunks':self.act_chunks,'measured_work_goals':self.stage,'task_success_not_inferred_from_ACK':True}
        return copy.deepcopy(self._score_cache) if self._score_cache else {'valid':False,'success':None,'control_steps':self.steps,'measured_work_goals':self.stage}
    def visibility(self):
        """Private availability audit, zero physics steps, never a model tool."""
        import mujoco
        rows=[];raster=[]
        for name in ['agentview','robot0_eye_in_hand']:
            seg=np.asarray(self.sim.render(camera_name=name,width=256,height=256,segmentation=True))
            axis=min([0,1],key=lambda i:len(np.unique(seg[...,i])));raster.append((name,seg[...,1-axis],seg[...,axis]))
        for item in self.objects:
            for field in ('mark','lot'):
                ids=[self.sim.model.geom_name2id('pack_'+item+'_mark')] if field=='mark' else [self.sim.model.geom_name2id('pack_'+item+'_lot_base')]+[self.sim.model.geom_name2id('pack_'+item+'_lot_'+s) for s in LETTERS[self.truth['items'][item]['lot']]]
                pixels={};raw={}
                model=getattr(self.sim.model,'_model',self.sim.model);data=getattr(self.sim.data,'_data',self.sim.data)
                for name,geom,typ in raster:
                    coords=np.argwhere(np.isin(geom,ids)&(typ==5));raw[name]=len(coords)
                    camera=self.sim.model.camera_name2id(name);origin=np.asarray(self.sim.data.cam_xpos[camera]);rotation=np.asarray(self.sim.data.cam_xmat[camera]).reshape(3,3)
                    f=128/np.tan(np.deg2rad(self.sim.model.cam_fovy[camera])/2);group=np.asarray(self.sim._render_context_offscreen.vopt.geomgroup,dtype=np.uint8)
                    counts=[]
                    for flip in [False,True]:
                        n=0
                        for v,u in coords:
                            yy=255-v if flip else v;direction=rotation@np.array([(u+.5-128)/f,(yy+.5-128)/f,-1.]);direction/=np.linalg.norm(direction);hit=np.array([-1],np.int32)
                            mujoco.mj_ray(model,data,origin,direction,group,1,-1,hit);n+=int(hit[0] in ids)
                        counts.append(n)
                    pixels[name]=max(counts)
                rows.append({'item':item,'field':field,'pixels':pixels,'raw_segmentation_pixels':raw,'scope':'camera ray agrees with original segmentation; availability, not model interpretation'})
        return rows
    def close(self):
        if not self.closed:self.native.close();self.closed=True
