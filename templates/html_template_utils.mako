<%! import pygal %>


<%def name="get_custom_style()">
<%
    custom_style = pygal.style.Style()
    custom_style.label_font_size = 15
    custom_style.value_font_size = 20
    custom_style.value_label_font_size = 20
    custom_style.major_label_font_size = 18
    custom_style.tooltip_font_size = 20
    custom_style.title_font_size = 25
    custom_style.legend_font_size = 20
    return custom_style
%>
</%def>

<%def name="chart_horizontal_bar(descriptions, values, title=None)">
<%
    chart = pygal.HorizontalBar()
    chart.title = title
    for i in xrange(0, len(descriptions)):
        chart.add(descriptions[i], values[i])
%>
${chart.render(is_unicode=True, disable_xml_declaration=True, style=get_custom_style())}
</%def>

<%def name="chart_one_line(descriptions, values, title=None)">
<%
    chart = pygal.Line()
    chart.title = title
    chart.x_labels = descriptions
    chart.add(None, values)
%>
${chart.render(is_unicode=True, disable_xml_declaration=True, style=get_custom_style())}
</%def>