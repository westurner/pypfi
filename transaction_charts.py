#!/usr/bin/env python
from __future__ import print_function
import calendar
import cgi
import collections
import sys
import StringIO
import numpy as np
import pandas as pd

def configure_pandas_print_options():
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

configure_pandas_print_options()

DAY_ABBRS = dict(enumerate(calendar.day_abbr))

def get_weekday_name(n):
    return "%d-%s" % (n, DAY_ABBRS.get(n))

HTML_HEADER="""
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.0/css/bootstrap.min.css">
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.0/css/bootstrap-theme.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jquery.tocify/1.9.0/stylesheets/jquery.tocify.css">

<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.0/js/bootstrap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.11.2/jquery-ui.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.tocify/1.9.0/javascripts/jquery.tocify.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/floatthead/1.2.8/jquery.floatThead.min.js"></script>

<script>
$(document).ready(function() {
    $("table.table").floatThead();
    $('h2,h3,h4,h5,h6').css('display', 'inline-table').after('<a class="headerlink" href="#">^</a>');
    $("#toc").tocify({
        selectors: "h2,h3,h4,h5,h6",
        showAndHide: false,
        hashGenerator: "pretty",
        scrollHistory: true,
        extendPage: false
        });
});
</script>

<style>
.table-condensed>thead>tr>th,
.table-condensed>tbody>tr>th,
.table-condensed>tfoot>tr>th,
.table-condensed>thead>tr>td,
.table-condensed>tbody>tr>td,
.table-condensed>tfoot>tr>td {
    padding: 2px !important;
}

table.floatThead-table {
    border-top: none;
    border-bottom: none;
    background-color: #FFF;
}

.tocify {
   position: static;
   margin-left: 0;
}

.tocify-subheader {
    text-indent: 20px;
    display: inherit !important;
}

a.headerlink {
    color: #F2F2F2;
    padding: 0 4px 0 4px;
    text-decoration: none;
}

</style>
"""


class ReportDict(object):
    def __init__(self, headingchar='-', headinghtml='h3'):
        self.headingchar = headingchar
        self.headinghtml = headinghtml
        self._dict = collections.OrderedDict()

    def add_report(self, name, value):
        if name in self._dict:
            raise KeyError(name)
        self._dict[name] = value

    __setitem__ = add_report

    def __getitem__(self, key):
        return self._dict.__getitem__(key)

    def to_str_iter(self):
        for key, value in self._dict.iteritems():
            yield key
            yield self.headingchar * len(key)
            if hasattr(value, 'to_string'):
                yield value.to_string(na_rep='')
            else:
                yield str(value)
            yield '\n'

    def __str__(self):
        return u'\n'.join(self.to_str_iter())

    def print_str(self, output=sys.stdout):
        for line in self.to_str_iter():
            print(line, file=output)

    def to_html_iter(self):
        for key, value in self._dict.iteritems():
            yield '<div class="{0}">'.format(cgi.escape(key))
            yield '<{0}>{1}</{0}>'.format(self.headinghtml, cgi.escape(key))
            if isinstance(value, ReportDict):
                for line in value.to_html_iter():
                    yield line
            else:
                if hasattr(value, 'to_html'):
                    yield '<div class="table-responsive">'
                    yield value.to_html(na_rep='', classes='table table-condensed table-hover table-bordered table-striped')
                    yield '</div>'
                else:
                    yield '<pre class="pandas_str">\n{}\n</pre>'.format(cgi.escape(value))
            yield '</div>'

    def print_html(self, output=sys.stdout):
        for line in self.to_html_iter():
            print(line, file=output)



def read_transactions_tsv(path):
    df = pd.read_csv(path,
                    sep='\t',
                    #index_col=0,
                    parse_dates=['date'],
                    names=['date', 'desc', 'amount', 'balance'],
                    thousands=',')
    return df


def add_computed_columns(df):
    df['year'] = df['date'].apply(lambda x: x.year)
    df['yearmonth'] = df['date'].apply(lambda x: "%d-%02d" % (x.year, x.month))
    df['month'] = df['date'].apply(lambda x: x.month)
    df['weekday'] = df['date'].apply(lambda x: x.weekday())
    df['weekday_abbr'] = df['weekday'].apply(get_weekday_name)
    df['hour'] = df['date'].apply(lambda x: x.hour)
    return df


def with_groupby(df, _output=sys.stdout):
    output = ReportDict()

    df = add_computed_columns(df)
    # output['df'] = df

    by_year = df.groupby(df['year'], as_index=True)['amount'].sum()
    output['groupby_year'] = by_year

    by_yearmonth = df.groupby(df['yearmonth'], as_index=True)['amount'].sum()
    output['groupby_yearmonth'] = by_yearmonth

    by_month = df.groupby(df['month'], as_index=True)['amount'].sum()
    output['groupby_month'] = by_month

    by_weekday = df.groupby(df['weekday_abbr'], as_index=True)['amount'].sum()
    output['groupby_weekday'] = by_weekday

    by_hour = df.groupby(df['hour'], as_index=True)['amount'].sum()
    output['groupby_hour'] = by_hour

    return output


def with_pivot(df, _output=sys.stdout):
    output = ReportDict()

    df = add_computed_columns(df)
    # create a unique index
    #df['index'] = df['date'].apply(str) + ',' + df.index.astype('str')

    df['index'] = df.index
    # output['df-'] = df  # see: footer


    df_year = pd.pivot_table(df,
                             index=['date', 'index'],
                             columns='year',
                             values='amount',
                             aggfunc=np.sum,
                             margins=True)
    output['pivot_by_year'] = df_year

    df_year_describe = df_year.describe()
    output['pivot_by_year.describe()'] = df_year_describe

    df_year_sum = df_year.sum()
    output['pivot_by_year.sum()'] = df_year_sum


    df_yearmonth = pd.pivot_table(df,
                                  index=['date', 'index'],
                                  columns=['year','month'],
                                  values='amount',
                                  aggfunc=np.sum,
                                  margins=True)
    output['pivot_by_yearmonth'] = df_yearmonth

    df_yearmonth_describe = df_yearmonth.describe()
    output['pivot_by_yearmonth.describe()'] = df_yearmonth_describe

    df_yearmonth_sum = df_yearmonth.sum()
    output['pivot_by_yearmonth.sum()'] = df_yearmonth_sum


    df_weekday = pd.pivot_table(df,
                                index=['date', 'index'],
                                columns='weekday_abbr',
                                values='amount',
                                aggfunc=np.sum,
                                margins=True)
    output['pivot_by_weekday'] = df_weekday

    by_weekday_describe = df_weekday.describe()
    output['pivot_by_weekday.describe()'] = by_weekday_describe

    by_weekday_sum = df_weekday.sum()
    output['pivot_by_weekday.sum()'] = by_weekday_sum


    df_hour = pd.pivot_table(df,
                             index=['date', 'index'],
                             columns='hour',
                             values='amount',
                             aggfunc=np.sum,
                             margins=True)
    output['pivot_by_hour'] = df_hour

    df_hour_describe = df_hour.describe()
    output['pivot_by_hour.describe()'] = df_hour_describe

    df_hour_sum = df_hour.sum()
    output['pivot_by_hour.sum()'] = df_hour_sum

    output['df-'] = df

    return output


def main():
    input_file = './transactions.tsv'
    output_file = './test.html'
    debug = True

    output = sys.stdout
    output = StringIO.StringIO()

    df = read_transactions_tsv(input_file)
    print(df, file=output)
    print(df.dtypes, file=output)


    output_data = ReportDict(headingchar='=', headinghtml='h2')
    output_data['df'] = df.copy()

    output_data['with_groupby'] = with_groupby(df, _output=output)
    output_data['with_pivot'] = with_pivot(df, _output=output)

    if debug:
        output_data.print_str()

    import codecs
    with codecs.open(output_file, 'w', encoding='utf8') as f:
        f.write('<html><head>')
        f.write('<title>{0}</title>'.format(cgi.escape(input_file)))
        f.write(HTML_HEADER)
        f.write('</head><body>')
        f.write('<div class="container">')
        f.write('<div class="row">')

        f.write('<div class="page-header">')
        f.write('<h1>{0}</h1>'.format(cgi.escape(input_file)))
        f.write('</div>')

        f.write('<div id="toc"></div>')

        f.write('<div class="body">')
        output_data.print_html(output=f)
        f.write('</div>')

        f.write('</div>')
        f.write('</div>')
        f.write('<div class="footer"><div class="container"><div class="row">')
        f.write('<p class="text-muted">{0}</p>'.format(cgi.escape(input_file)))
        f.write('<a class="headerlink" href="#">^top^</a>')
        f.write('</div></div></div>')
        f.write('</body></html>')

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
