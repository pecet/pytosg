<%! import calendar %>
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <title>pytosg output</title>

        <!-- Bootstrap stuff -->
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    </head>
    <body>
        <div class="jumbotron text-center">
            <h1>pytosg output</h1>
        </div>

        <div class="container">
            <div class="row">
                <div class="col-md-4">
                    <h3>Total tweets</h3>
                    <p class="text-left">${d['tweet_count_total']}</p>
                </div>
                <div class="col-md-4">
                    <h3>Tweets per year</h3>
                    <table class="table table-striped">
                        <thead>
                            <tr>
                            <th>Year</th><th>Tweet count</th><th>Percentage of total</th>
                            </tr>
                        </thead>
                        <tbody>
                            %for year, year_count in d['tweet_count_per_year'].items():
                            <tr>
                                <td>${year}</td><td>${year_count}</td><td>${round(float(year_count) / float(d['tweet_count_total']) * 100, 1)}%</td>
                            </tr>
                            %endfor
                        </tbody>
                    </table>

                </div>
                <div class="col-md-4">
                    <h3>Tweets per month</h3>
                    <table class="table table-striped">
                        <thead>
                            <tr>
                            <th>Month</th><th>Tweet count</th><th>Percentage of total</th>
                            </tr>
                        </thead>
                        <tbody>
                            %for month, month_count in d['tweet_count_per_month'].items():
                            <tr>
                                <td>${calendar.month_name[month]}</td><td>${month_count}</td><td>${round(float(month_count) / float(d['tweet_count_total']) * 100, 1)}%</td>
                            </tr>
                            %endfor
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

    </body>
</html>