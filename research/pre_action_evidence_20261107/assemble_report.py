from pathlib import Path
ROOT=Path(__file__).resolve().parent
parts=[('第一部分：研究定位、方法边界与实施','editorial_core.md'),('第二部分：具体benchmark、任务与指标协议','design/benchmark_protocol.md'),('第三部分：相关工作核验与候选方法','design/methods_and_related_work.md'),('第四部分：Codex实现蓝图','design/implementation_blueprints.md'),('附录A：参考文献与固定版本','design/reference_bibliography.md')]
if (ROOT/'DELIVERY_STATUS.md').exists():parts.append(('附录B：工程状态与验证边界','DELIVERY_STATUS.md'))
sections=[]
for title,rel in parts:
    text=(ROOT/rel).read_text(encoding='utf-8').splitlines()
    if text and text[0].startswith('# '):text=text[1:]
    sections.append('# '+title+'\n\n'+'\n'.join(text).strip())
(ROOT/'REPORT.md').write_text('\n\n'.join(sections)+'\n',encoding='utf-8')
print('Report assembled')
