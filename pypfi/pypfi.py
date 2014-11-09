#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
"""
pypfi
"""
import calendar
import cgi
import codecs
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


DAY_ABBRS = dict(enumerate(calendar.day_abbr))


def get_weekday_name(n):
    """
    Args:
        n (int): integer weekday name (pandas)
    Returns:
        str: naturally-sortable string: ``0-Mon``, ``6-Sun``
    """
    return "%d-%s" % (n, DAY_ABBRS.get(n))


def add_computed_columns(df, colname='date'):
    """
    Add computed columns to a dataframe for date-based calculations

    Args:
        df (pandas.DataFrame): DataFrame to augment
    Returns:
        df (pandas.DataFrame): dataframe with columns added

    .. note:: This method modifies the ``df`` argument
       (does not do ``df.copy()`` before adding computed columns)

    """
    df['year'] = df[colname].apply(lambda x: x.year)
    df['yearmonth'] = df[colname].apply(lambda x: "%d-%02d" % (x.year, x.month))
    df['month'] = df[colname].apply(lambda x: x.month)
    df['weekday'] = df[colname].apply(lambda x: x.weekday())
    df['weekday_abbr'] = df['weekday'].apply(get_weekday_name)
    df['hour'] = df[colname].apply(lambda x: x.hour)
    return df


def build_groupby_reports(df, _output=sys.stdout):
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


def build_pivot_reports(df, _output=sys.stdout):
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

   width: inherit;
   max-height: inherit;
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


def write_html_report(input_file, output_file, report_dict):
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
        report_dict.print_html(output=f)
        f.write('</div>')

        f.write('</div>')
        f.write('</div>')
        f.write('<div class="footer"><div class="container"><div class="row">')
        f.write('<p class="text-muted">{0}</p>'.format(cgi.escape(input_file)))
        f.write('<a class="headerlink" href="#">^top^</a>')
        f.write('</div></div></div>')
        f.write('</body></html>')


def pypfi(input_file, output_file, debug=False, output=sys.stdout):

    df = read_transactions_tsv(input_file)
    if debug:
        print(df, file=output)
        print(df.dtypes, file=output)

    report_dict = ReportDict(headingchar='=', headinghtml='h2')
    report_dict['df'] = df.copy()

    report_dict['build_groupby_reports'] = build_groupby_reports(df, _output=output)
    report_dict['build_pivot_reports'] = build_pivot_reports(df, _output=output)

    if debug:
        report_dict.print_str(output=output)

    write_html_report(input_file, output_file, report_dict)

    return 0



import unittest
class Test_pypfi(unittest.TestCase):
    def test_pypfi(self):
        pass


def main(*args):
    import logging
    import optparse
    import sys

    prs = optparse.OptionParser(
        usage="%prog -i <input.tsv> -o <report.html>")

    prs.add_option('-i', '--input-file',
                   dest='input_file',)
    prs.add_option('-o', '--output-file',
                   dest='output_file',)

    prs.add_option('-v', '--verbose',
                    dest='verbose',
                    action='store_true',)
    prs.add_option('-q', '--quiet',
                    dest='quiet',
                    action='store_true',)
    prs.add_option('-t', '--test',
                    dest='run_tests',
                    action='store_true',)

    args = args and list(args) or sys.argv[1:]
    (opts, args) = prs.parse_args(args)

    if not opts.quiet:
        logging.basicConfig()

        if opts.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

    if opts.run_tests:
        sys.argv = [sys.argv[0]] + args
        import unittest
        exit(unittest.main())

    if opts.verbose:
        debug = True
        output = sys.stdout
    else:
        debug = False
        output = StringIO.StringIO()

    return pypfi(opts.input_file,
                 opts.output_file,
                 debug=debug,
                 output=output)


if __name__ == "__main__":
    import sys
    sys.exit(main())
