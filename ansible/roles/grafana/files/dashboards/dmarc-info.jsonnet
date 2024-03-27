local grafana = import 'grafonnet/grafana.libsonnet';

grafana.dashboard.new(
  'DMARC Info',
  schemaVersion=16,
  uid='dmarc-info',
  time_from='now-7d',
).addTemplate(
  grafana.template.new(
    'domain',
    'dmarc InfluxDB',
    'SHOW TAG VALUES WITH key = "domain"',
    refresh='time',
    current='umich.edu',
    sort=1,
  )
).addPanel(
  grafana.graphPanel.new(
    'Message Count',
    datasource='dmarc InfluxDB',
    interval='1d',
    legend_show=false,
  ).addTarget(
    grafana.influxdb.target(
      'SELECT sum("count") FROM "dmarc_report" WHERE ("domain" = \'$domain\') AND $timeFilter GROUP BY time($__interval) fill(none)',
    )
  ),
  { x: 0, y: 0, w: 12, h: 10 },
).addPanel(
  grafana.graphPanel.new(
    'DMARC',
    datasource='dmarc InfluxDB',
    interval='1d',
    legend_show=false,
    lines=false,
    bars=true,
    percentage=true,
    max=100,
    stack=true,
    aliasColors={ 'false': 'red', 'true': 'green' },
  ).addTarget(
    grafana.influxdb.target(
      'SELECT sum("count") FROM "dmarc_report" WHERE ("domain" = \'$domain\') AND $timeFilter GROUP BY time($__interval), "aligned_dmarc" fill(none)',
      alias='$tag_aligned_dmarc',
    )
  ),
  { x: 12, y: 0, w: 12, h: 10 },
).addPanel(
  grafana.graphPanel.new(
    'DKIM',
    datasource='dmarc InfluxDB',
    interval='1d',
    legend_show=false,
    lines=false,
    bars=true,
    percentage=true,
    max=100,
    stack=true,
    aliasColors={ 'false': 'red', 'true': 'green' },
  ).addTarget(
    grafana.influxdb.target(
      'SELECT sum("count") FROM "dmarc_report" WHERE ("domain" = \'$domain\') AND $timeFilter GROUP BY time($__interval), "aligned_dkim" fill(none)',
      alias='$tag_aligned_dkim',
    )
  ),
  { x: 0, y: 10, w: 12, h: 10 },
).addPanel(
  grafana.graphPanel.new(
    'SPF',
    datasource='dmarc InfluxDB',
    interval='1d',
    legend_show=false,
    lines=false,
    bars=true,
    percentage=true,
    max=100,
    stack=true,
    aliasColors={ 'false': 'red', 'true': 'green' },
  ).addTarget(
    grafana.influxdb.target(
      'SELECT sum("count") FROM "dmarc_report" WHERE ("domain" = \'$domain\') AND $timeFilter GROUP BY time($__interval), "aligned_spf" fill(none)',
      alias='$tag_aligned_spf',
    )
  ),
  { x: 12, y: 10, w: 12, h: 10 },
).addPanel(
  grafana.tablePanel.new(
    'Top Failed Domains',
    datasource='dmarc InfluxDB',
    sort='count',
  ).addTarget(
    grafana.influxdb.target(
      'SELECT top("sum", 24) as "count", "src_domain" FROM (SELECT sum("count") FROM "dmarc_report" WHERE ("domain" = \'$domain\') AND ("aligned_dmarc" = \'false\') AND $timeFilter GROUP BY "src_domain")',
      resultFormat='table',
    )
  ).hideColumn('Time'),
  { x: 0, y: 20, w: 6, h: 10 },
).addPanel(
  grafana.tablePanel.new(
    'Top Reporters of Failures',
    datasource='dmarc InfluxDB',
    sort='count',
  ).addTarget(
    grafana.influxdb.target(
      'SELECT top("sum", 24) as count, "org" FROM (SELECT sum("count") FROM "dmarc_report" WHERE ("domain" = \'$domain\') AND ("aligned_dmarc" = \'false\') AND $timeFilter GROUP BY "org")',
      resultFormat='table',
    )
  ).hideColumn('Time'),
  { x: 6, y: 20, w: 6, h: 10 },
).addPanel(
  grafana.tablePanel.new(
    'Top SPF Failures/Misalignments',
    datasource='dmarc InfluxDB',
    sort='count',
  ).addTarget(
    grafana.influxdb.target(
      'SELECT top("sum", 24) as count, "src_domain" FROM (SELECT sum("count") FROM "dmarc_report" WHERE ("domain" = \'$domain\') AND ("aligned_spf" = \'false\') AND $timeFilter GROUP BY "src_domain")',
      resultFormat='table',
    )
  ).hideColumn('Time'),
  { x: 12, y: 30, w: 6, h: 10 },
).addPanel(
  grafana.tablePanel.new(
    'Top DKIM Failures/Misalignments',
    datasource='dmarc InfluxDB',
    sort='count',
  ).addTarget(
    grafana.influxdb.target(
      'SELECT top("sum", 24) as count, "src_domain" FROM (SELECT sum("count") FROM "dmarc_report" WHERE ("domain" = \'$domain\') AND ("aligned_dkim" = \'false\') AND $timeFilter GROUP BY "src_domain")',
      resultFormat='table',
    )
  ).hideColumn('Time'),
  { x: 18, y: 30, w: 6, h: 10 },
)
