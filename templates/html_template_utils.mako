<%! import pygal %>

<%def name="chart_horizontal_bar(title, descriptions, values)">
<%
    chart = pygal.HorizontalBar()
    chart.title = title
    for i in xrange(0, len(descriptions)):
        chart.add(descriptions[i], values[i])
%>
${chart.render(is_unicode=True, disable_xml_declaration=True).replace(u'\xa9','')}
</%def>
