"""Render the reviewed Markdown research package; no remote/model access."""
import re, html, json, hashlib
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle, PageBreak, KeepTogether, Flowable

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'artifacts'; OUT.mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont('CN','C:/Windows/Fonts/msyh.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('CNB','C:/Windows/Fonts/msyhbd.ttc',subfontIndex=0))
pdfmetrics.registerFontFamily('CN',normal='CN',bold='CNB',italic='CN',boldItalic='CNB')
NAVY=colors.HexColor('#15334C'); TEAL=colors.HexColor('#006F78'); INK=colors.HexColor('#253545')
BODY=ParagraphStyle('body',fontName='CN',fontSize=9.8,leading=16.4,spaceAfter=7.2,textColor=INK,wordWrap='CJK')
CELL=ParagraphStyle('cell',parent=BODY,fontSize=7.5,leading=11.5,spaceAfter=2)
SMALL=ParagraphStyle('small',parent=BODY,fontSize=8.2,leading=13,textColor=colors.HexColor('#536578'))
H1=ParagraphStyle('h1',parent=BODY,fontName='CNB',fontSize=17,leading=24,spaceBefore=10,spaceAfter=12,textColor=NAVY,keepWithNext=True)
H2=ParagraphStyle('h2',parent=BODY,fontName='CNB',fontSize=13,leading=20,spaceBefore=12,spaceAfter=8,textColor=TEAL,keepWithNext=True)
H3=ParagraphStyle('h3',parent=BODY,fontName='CNB',fontSize=10.5,leading=17,spaceBefore=8,spaceAfter=5,textColor=NAVY,keepWithNext=True)
CODE=ParagraphStyle('code',parent=BODY,fontSize=8,leading=12,backColor=colors.HexColor('#F0F5F8'),leftIndent=8,rightIndent=6,spaceBefore=4,spaceAfter=5)

def inline(s):
    s=html.escape(s)
    s=re.sub(r'\[([^\]]+)\]\((https?://[^\s)]+)\)',lambda m:'<link href="'+m.group(2)+'" color="#006F78">'+m.group(1)+'</link>',s)
    s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'`([^`]+)`',r'<font color="#006F78">\1</font>',s)
    return s

class Architecture(Flowable):
    def __init__(self):super().__init__();self.width=480;self.height=215
    def draw(self):
        c=self.canv; boxes=[('公开RGB / 本体 / 普通反馈',0,174,480,30),('公共证据仓：来源 · 时间 · 对象绑定 · 未知',0,128,480,30),('Codex：需求 / 候选操作 / A或B研究插件',0,82,480,30),('公共校验 → 原工具适配器 → 冻结 π0.5',0,36,480,30)]
        for label,x,y,w,h in boxes:
            c.setFillColor(colors.HexColor('#EDF5F7'));c.setStrokeColor(TEAL);c.roundRect(x,y,w,h,5,fill=1,stroke=1)
            c.setFillColor(NAVY);c.setFont('CN',10);c.drawCentredString(x+w/2,y+10,label)
        for y in [169,123,77]:
            c.setStrokeColor(TEAL);c.line(240,y,240,y-9);c.line(240,y-9,236,y-5);c.line(240,y-9,244,y-5)
        c.setFont('CN',8);c.setFillColor(INK);c.drawString(0,8,'评分与未来分支仅在独立评价/开发通道；不进入policy上下文。')

def parse(text):
    result=[];lines=text.splitlines();i=0;code=False;ref_mode=False
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('```'):
            block=[];i+=1
            while i<len(lines) and not lines[i].strip().startswith('```'):
                block.append(lines[i]);i+=1
            i+=1
            # Keep long code/trees breakable and CJK-safe, rather than clipping a Preformatted block.
            for s in block:result.append(Paragraph(inline(s).replace(' ','&#160;') or '&#160;',CODE))
            continue
        if line.startswith('|') and i+1<len(lines) and re.match(r'^\|[\s:|\-]+\|$',lines[i+1].strip()):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                row=lines[i].strip()
                if not re.match(r'^\|[\s:|\-]+\|$',row):rows.append([Paragraph(inline(x.strip()),CELL) for x in row.strip('|').split('|')])
                i+=1
            n=max(map(len,rows)); widths=[480/n]*n
            table=LongTable(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#DCECF0')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.6,TEAL),('GRID',(0,1),(-1,-1),.25,colors.HexColor('#CFDDE5')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
            result.extend([table,Spacer(1,9)]);continue
        m=re.match(r'^(#{1,4})\s+(.*)',line)
        if m:
            level=len(m.group(1));title=m.group(2)
            if level==1:
                ref_mode='附录A' in title
                result.append(PageBreak())
                result.append(Paragraph(inline(title),H1))
            else:result.append(Paragraph(inline(title),H2 if level==2 else H3))
            i+=1;continue
        # Join multiline paragraph, keeping lists as separate readable entries.
        p=[line];i+=1
        if not re.match(r'^([-*]|\d+\.)\s',line):
            while i<len(lines) and lines[i].strip() and not re.match(r'^(#|```|\||[-*]\s|\d+\.\s)',lines[i].strip()):p.append(lines[i].strip());i+=1
        result.append(Paragraph(inline(' '.join(p)),SMALL if ref_mode else BODY))
    return result

def footer(c,doc):
    c.saveState();w,h=A4
    c.setStrokeColor(colors.HexColor('#D3DFE6'));c.line(57,42,w-57,42)
    c.setFont('CN',8);c.setFillColor(colors.HexColor('#60778A'));c.drawString(57,29,'行动前证据保全 · 研究协议与实施 v1 · 2026-11-07');c.drawRightString(w-57,29,str(doc.page));c.restoreState()

def main():
    target=OUT/'长程机器人行动前证据保全研究报告_完善版_20261107.pdf'
    doc=SimpleDocTemplate(str(target),pagesize=A4,rightMargin=57,leftMargin=57,topMargin=56,bottomMargin=57,title='长程机器人行动前证据保全：研究协议与技术路线',author='Research study / Codex assisted preparation')
    story=[Spacer(1,38),Paragraph('面向长程机器人任务的',H1),Paragraph('行动前证据保全研究',ParagraphStyle('title',parent=H1,fontSize=25,leading=35)),Spacer(1,16),Paragraph('开题报告完善版',H2),Paragraph('具体测试任务 · 机制指标 · Codex skill/harness · 冻结 π0.5',BODY),Spacer(1,22),Architecture(),Spacer(1,18),Paragraph('研究目标：在行动改变信息条件之前，保留未来作出正确选择的能力。',BODY),Paragraph('本文提供预注册候选与公共基础设施，不将拟议贡献、CPU通过或接口验证表述为已取得的研究效果。原始五页报告保持不变。',SMALL),Spacer(1,14),Paragraph('2026年11月7日 / 版本1 / 原生任务与新增诊断协议分表',SMALL),PageBreak()]
    story.append(Paragraph('阅读导航',H1))
    for s in ['第一部分：研究问题、可证伪假设、现有日志、统一控制与实施里程碑。','第二部分：五benchmark精确任务面板、开发/留出、EVID-Preserve扩展、指标公式与统计。','第三部分：原报告文献核验、HexaShell v3与三条方法路线、可复现边界。','第四部分：Codex实现蓝图、契约示例、接线顺序与研发扩展口。','附录：本次实际完成的配置、测试和同步收据。']:
        story.append(Paragraph(s,BODY))
    story.append(Spacer(1,12));story.append(Paragraph('建议顺序：先测量与强对照，再实现行动条件化预测；最后才做离线价值学习。',H2))
    story.extend(parse((ROOT/'REPORT.md').read_text(encoding='utf-8')))
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    from pypdf import PdfReader
    r=PdfReader(target);text=''.join(p.extract_text() or '' for p in r.pages)
    receipt={'pdf':target.name,'pages':len(r.pages),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'text_chars':len(text),'source_report_sha256':json.loads((ROOT/'source_receipt.json').read_text(encoding='utf-8'))['sha256'],'original_preserved':True,'visual_QA':'PENDING_RENDER_INSPECTION'}
    (OUT/'pdf_build_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(receipt,ensure_ascii=False))

if __name__=='__main__':main()
