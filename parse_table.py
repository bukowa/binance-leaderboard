import pandas as pd
from binance.common.common import load_json

positions = load_json('./binance/positions.json')
performance = load_json('./binance/traders_performance.json')

uuid_performance = {
    p['uid']: p['performanceRetList'] for p in performance
}

for i, pos, in enumerate(positions):
    perf_list = uuid_performance[positions[i]['uuid']]

    for perf in perf_list:
        if perf['periodType'] == 'ALL' and perf['statisticsType'] == 'PNL':
            total_pnl = perf['value']
        if perf['periodType'] == 'ALL' and perf['statisticsType'] == 'ROI':
            total_roi = perf['value']

    positions[i]['total_pnl'] = total_pnl
    positions[i]['total_roi'] = total_roi * 100


df = pd.DataFrame(positions)

def get(index, key):
    return df.loc[index, key]


def set(index, key, value):
    df.loc[index, key] = value


for i in range(len(df)):
    pnl = get(i, "pnl")
    set(i, "pnl", f"{pnl:.2f}")

    roe = get(i, "roe")
    set(i, "roe", f"{roe:.3f}")

    markPrice = get(i, "markPrice")
    if int(markPrice) > 0:
        set(i, "markPrice", f"{markPrice:.2f}")

    entryPrice = get(i, "entryPrice")
    if int(entryPrice) > 0:
        set(i, "entryPrice", f"{entryPrice:.2f}")

    total_pnl = get(i, "total_pnl")
    if int(entryPrice) > 0:
        set(i, "total_pnl", f"{total_pnl:.2f}")

    user = get(i, "uuid")
    set(
        i,
        "user",
        f'<a href="https://www.binance.com/en/futures-activity/leaderboard/user/um?encryptedUid={user}" target="_blank">click</a>',
    )

    set(i, "amount", str(get(i, "amount")))

columns = [
        "symbol",
        "amount",
        "pnl",
        "roe",
        "entryPrice",
        "markPrice",
        "leverage",
        "updateTime",
        "total_pnl",
        "total_roi",
        "user",
    ]

df = df.reindex(columns=columns)

html = df.to_html(
    header=True, classes="my-table table table-bordered table-striped", escape=False
)
html = "\n".join(html.splitlines()[:-1])
pager = f"""
  <tfoot>
    <tr>
      <th colspan="155" class="ts-pager">
        <div class="form-inline">
          <div class="btn-group btn-group-sm mx-1" role="group">
            <button type="button" class="btn btn-secondary first" title="first">⇤</button>
            <button type="button" class="btn btn-secondary prev" title="previous">←</button>
          </div>
          <span class="pagedisplay"></span>
          <div class="btn-group btn-group-sm mx-1" role="group">
            <button type="button" class="btn btn-secondary next" title="next">→</button>
            <button type="button" class="btn btn-secondary last" title="last">⇥</button>
          </div>
          <select class="form-control-sm custom-select px-1 pagesize" title="Select page size">
            <option selected="selected" value="10">10</option>
            <option value="20">20</option>
            <option value="30">30</option>
            <option value="all">All Rows</option>
          </select>
          <select class="form-control-sm custom-select px-4 mx-1 pagenum" title="Select page number"></select>
        </div>
      </th>
    </tr>
  </tfoot>
  </table>
"""

script = """
$(function() {

  $("table").tablesorter({
    theme : "bootstrap",

    widthFixed: true,

    // widget code contained in the jquery.tablesorter.widgets.js file
    // use the zebra stripe widget if you plan on hiding any rows (filter widget)
    // the uitheme widget is NOT REQUIRED!
    widgets : [ "filter", "columns", "zebra" ],

    widgetOptions : {
      // using the default zebra striping class name, so it actually isn't included in the theme variable above
      // this is ONLY needed for bootstrap theming if you are using the filter widget, because rows are hidden
      zebra : ["even", "odd"],

      // class names added to columns when sorted
      columns: [ "primary", "secondary", "tertiary" ],

      // reset filters button
      filter_reset : ".reset",

      // extra css class name (string or array) added to the filter element (input or select)
      filter_cssFilter: [
        'form-control',
        'form-control',
        'form-control custom-select', // select needs custom class names :(
        'form-control',
        'form-control',
        'form-control',
        'form-control'
      ]

    }
  })
  .tablesorterPager({

    // target the pager markup - see the HTML block below
    container: $(".ts-pager"),

    // target the pager page select dropdown - choose a page
    cssGoto  : ".pagenum",

    // remove rows from the table to speed up the sort of large tables.
    // setting this to false, only hides the non-visible rows; needed if you plan to add/remove rows with the pager enabled.
    removeRows: false,

    // output string - default is '{page}/{totalPages}';
    // possible variables: {page}, {totalPages}, {filteredPages}, {startRow}, {endRow}, {filteredRows} and {totalRows}
    output: '{startRow} - {endRow} / {filteredRows} ({totalRows})'

  });

});
"""


body = f"""
<html>
<head>
<meta charset='utf-8'>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/4.6.2/css/bootstrap.min.css" integrity="sha512-rt/SrQ4UNIaGfDyEXZtNcyWvQeOq0QLygHluFQcSjaGB04IxWhal71tKuzP6K8eYXYB6vJV4pHkXcmFGGQ1/0w==" crossorigin="anonymous" referrerpolicy="no-referrer" />
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.3/jquery.min.js" integrity="sha512-STof4xm1wgkfm7heWqFJVn58Hm3EtS31XFaagaa8VMReCXAkQnJZ+jEy8PCC/iT18dFy95WcExNHFTqLyp72eQ==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.31.3/js/jquery.tablesorter.min.js" integrity="sha512-qzgd5cYSZcosqpzpn7zF2ZId8f/8CHmFKZ8j7mU4OUXTNRd5g+ZHBPsgKEwoqxCtdQvExE5LprwwPAgoicguNg==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.31.3/js/jquery.tablesorter.widgets.min.js" integrity="sha512-dj/9K5GRIEZu+Igm9tC16XPOTz0RdPk9FGxfZxShWf65JJNU2TjbElGjuOo3EhwAJRPhJxwEJ5b+/Ouo+VqZdQ==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.31.3/css/jquery.tablesorter.pager.min.css" integrity="sha512-TWYBryfpFn3IugX13ZCIYHNK3/2sZk3dyXMKp3chZL+0wRuwFr1hDqZR9Qd5SONzn+Lja10hercP2Xjuzz5O3g==" crossorigin="anonymous" referrerpolicy="no-referrer" />
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.31.3/js/extras/jquery.tablesorter.pager.min.js" integrity="sha512-y845ijdup9lDunrcSRQAlFdQICHVhkB5UNguWRX8A3L+guxO7Oow0poojw0PLckhcKij++h85bnyro80fjR9+A==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/4.6.2/js/bootstrap.min.js" integrity="sha512-7rusk8kGPFynZWu26OKbTeI+QPoYchtxsmPeBqkHIEXJxeun4yJ4ISYe7C6sz9wdxeE1Gk3VxsIWgCZTc+vX3g==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.31.3/css/theme.bootstrap_4.min.css" integrity="sha512-2C6AmJKgt4B+bQc08/TwUeFKkq8CsBNlTaNcNgUmsDJSU1Fg+R6azDbho+ZzuxEkJnCjLZQMozSq3y97ZmgwjA==" crossorigin="anonymous" referrerpolicy="no-referrer" />
<style>
.tablesorter-pager .btn-group-sm .btn {{
  font-size: 1.2em; /* make pager arrows more visible */
}}
</style>
</head>
<body>
{html}
{pager}
    <script>
    {script}
    </script>
</body>
</html>
"""

import htmlmin

print(htmlmin.minify(body))
