local grafana = import 'grafonnet/grafana.libsonnet';

grafana.dashboard.new(
  'DMARC Source Info',
  schemaVersion=16,
  uid='dmarc-src-info',
  time_from='now-7d',
).addTemplate(
  grafana.template.new(
    'domain',
    'dmarc InfluxDB',
    'SELECT DISTINCT("header_from") FROM (SELECT "header_from", "count" FROM "dmarc_report") WHERE $timeFilter',
    refresh='time',
    current='umich.edu',
    sort=1,
  )
).addTemplate(
  grafana.template.new(
    'src_domain',
    'dmarc InfluxDB',
    'SELECT DISTINCT("src_domain") FROM (SELECT "src_domain", "count" FROM "dmarc_report" WHERE ("header_from" = \'${domain:raw}\')) WHERE $timeFilter',
    refresh='time',
    current='umich.edu',
    sort=1,
  )
).addPanel(
  grafana.tablePanel.new(
    'Source IPs',
    datasource='dmarc InfluxDB',
  ).addTarget(
    grafana.influxdb.target(
      'SELECT "count", "src_ip", "src" FROM "dmarc_report" WHERE ("header_from" = \'$domain\') AND ("src_domain" = \'$src_domain\') AND $timeFilter fill(null)',
      resultFormat='table',
    )
  ).addTransformations(
    [
      grafana.transformation.new(
        id='groupBy',
        options={
          fields: {
            count: {
              operation: 'aggregate',
              aggregations: ['sum'],
            },
            src_ip: {
              operation: 'groupby',
              aggregations: [],
            },
            src: {
              operation: 'aggregate',
              aggregations: ['lastNotNull'],
            },
          },
        },
      ),
      grafana.transformation.new(
        id='sortBy',
        options={
          fields: {},
          sort: [
            {
              field: 'count (sum)',
              desc: true,
            },
          ],
        },
      ),
      grafana.transformation.new(
        id='organize',
        options={
          indexByName: {
            'count (sum)': 0,
            src_ip: 1,
            'src (lastNotNull)': 2,
          },
          renameByName: {
            'count (sum)': 'count',
            'src (lastNotNull)': 'src',
          },
        },
      ),
    ]
  ),
  { x: 0, y: 0, w: 12, h: 10 },
).addPanel(
  grafana.tablePanel.new(
    'Source IPs for DMARC failures',
    datasource='dmarc InfluxDB',
  ).addTarget(
    grafana.influxdb.target(
      'SELECT "count", "src_ip", "src" FROM "dmarc_report" WHERE ("header_from" = \'$domain\') AND ("src_domain" = \'$src_domain\') AND ("aligned_dmarc" = \'false\') AND $timeFilter fill(null)',
      resultFormat='table',
    )
  ).addTransformations(
    [
      grafana.transformation.new(
        id='groupBy',
        options={
          fields: {
            count: {
              operation: 'aggregate',
              aggregations: ['sum'],
            },
            src_ip: {
              operation: 'groupby',
              aggregations: [],
            },
            src: {
              operation: 'aggregate',
              aggregations: ['lastNotNull'],
            },
          },
        },
      ),
      grafana.transformation.new(
        id='sortBy',
        options={
          fields: {},
          sort: [
            {
              field: 'count (sum)',
              desc: true,
            },
          ],
        },
      ),
      grafana.transformation.new(
        id='organize',
        options={
          indexByName: {
            'count (sum)': 0,
            src_ip: 1,
            'src (lastNotNull)': 2,
          },
          renameByName: {
            'count (sum)': 'count',
            'src (lastNotNull)': 'src',
          },
        },
      ),
    ]
  ),
  { x: 12, y: 0, w: 12, h: 10 },
).addPanel(
  grafana.tablePanel.new(
    'DMARC failure details',
    datasource='dmarc InfluxDB',
  ).addTarget(
    grafana.influxdb.target(
      'SELECT "count", "envelope_from", "spf_raw_result", "spf_result", "dkim_domain", "dkim_selector", "dkim_raw_result", "dkim_result", "org", "src", "src_ip" FROM "dmarc_report" WHERE ("header_from" = \'$domain\') AND ("src_domain" = \'$src_domain\') AND ("aligned_dmarc" = \'false\') AND $timeFilter fill(null)',
      resultFormat='table',
    )
  ).addTransformations(
    [
      grafana.transformation.new(
        id='sortBy',
        options={
          fields: {},
          sort: [
            {
              field: 'count',
              desc: true,
            },
          ],
        },
      ),
    ]
  ),
  { x: 0, y: 12, w: 24, h: 10 },
)
