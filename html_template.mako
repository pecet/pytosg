<html>
    <head>
        <title>pytosg output</title>
    </head>
    <body>
        Total number of tweets: ${tweet_count_total}

        <table>
            <tr>
                <th>Year</th><th>Month</th><th>Tweet count</th>
            </tr>
            %for year, year_count in tweet_count_per_year.items():
                <tr>
                    <th>${year}</th><th></th><th>${year_count}</th>
                </tr>
                %for month, month_count in tweet_count_per_year_month[year].items():
                <tr>
                    <td>${year}</td><td>${month}</td><td>${month_count}</td>
                <tr>
                %endfor
            %endfor

        </table>
    </body>
</html>