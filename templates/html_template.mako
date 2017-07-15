<%! import calendar
day_name = calendar.day_name[6:] + calendar.day_name[:6]
%>
<%namespace file="html_template_utils.mako" import="*"/>
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <title>pytosg output</title>
        <!-- Bootstrap stuff -->
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
        <script type="text/javascript" src="http://kozea.github.com/pygal.js/latest/pygal-tooltips.min.js"></script>
    </head>
    <body>
        <div class="jumbotron text-center">
            <h1>pytosg output</h1>
        </div>

        <div class="container">
            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading text-center"><h4>Total tweets</h4></div>
                    <div class="panel-body">
                        <div class="col-md-12">
                            <h2 class="text-center">${tweet_count_total}</h2>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading text-center"><h4>Tweets per day of the week</h4></div>
                    <div class="panel-body">
                        <div class="col-md-8">
                            ${chart_horizontal_bar(day_name, total_tweets_per_day_of_week.values())}
                        </div>
                        <div class="col-md-4">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                    <th>Day of the week</th><th>Tweet count</th><th>Percentage of total</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    %for day_of_week, day_of_week_count in total_tweets_per_day_of_week.items():
                                    <tr>
                                        <td>${day_name[day_of_week]}</td><td>${day_of_week_count}</td><td>${round(float(day_of_week_count) / float(tweet_count_total) * 100, 1)}%</td>
                                    </tr>
                                    %endfor
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading text-center"><h4>Tweets per month</h4></div>
                    <div class="panel-body">
                        <div class="col-md-8">
                            ${chart_horizontal_bar(calendar.month_name[1:], tweet_count_per_month.values())}
                        </div>
                        <div class="col-md-4">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                    <th>Month</th><th>Tweet count</th><th>Percentage of total</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    %for month, month_count in tweet_count_per_month.items():
                                    <tr>
                                        <td>${calendar.month_name[month]}</td><td>${month_count}</td><td>${round(float(month_count) / float(tweet_count_total) * 100, 1)}%</td>
                                    </tr>
                                    %endfor
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading text-center"><h4>Tweets per year</h4></div>
                    <div class="panel-body">
                        <div class="col-md-8">
                            ${chart_one_line(tweet_count_per_year.keys(), tweet_count_per_year.values())}
                        </div>
                        <div class="col-md-4">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                    <th>Year</th><th>Tweet count</th><th>Percentage of total</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    %for year, year_count in tweet_count_per_year.items():
                                    <tr>
                                        <td>${year}</td><td>${year_count}</td><td>${round(float(year_count) / float(tweet_count_total) * 100, 1)}%</td>
                                    </tr>
                                    %endfor
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="panel panel-default">
                    <div class="panel-heading text-center"><h4>Total tweets grouped by week of the year</h4></div>
                    <div class="panel-body">
                        <div class="col-md-12">
                           ${chart_one_line(map(lambda x: x[:-3] if "_00" in x else None,
                           cumulative_flat_tweet_count_per_year_week.keys()),
                           cumulative_flat_tweet_count_per_year_week.values(),
                           labels_major=tweet_count_per_year.keys(),
                           interpolate='cubic'
                           )}
                        </div>
                    </div>
                </div>
            </div>


        </div>

    </body>
</html>