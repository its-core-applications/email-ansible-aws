local grafana = import 'grafonnet/grafana.libsonnet';

grafana.dashboard.new(
  'Host Info',
  schemaVersion=16,
  uid='host-info',
  time_from='now-3h',
  refresh='5s',
).addTemplate(
  grafana.template.datasource(
    'INFLUX_DS',
    'influxdb',
    null,
    hide='label',
  )
).addTemplate(
  grafana.template.new(
    'entity',
    '$INFLUX_DS',
    'SELECT DISTINCT("sensu_entity_name") FROM (SELECT "1_min", "sensu_entity_name" FROM "load_avg" WHERE $timeFilter)',
    refresh='time',
    sort=1,
  )
).addPanel(
  grafana.graphPanel.new(
    'Available memory',
    datasource='$INFLUX_DS',
    legend_show=false,
    min=0,
    max=100,
    decimals=1,
  ).addTarget(
    grafana.influxdb.target(
      'SELECT (mean("memavailable") / mean("memtotal") * 100) AS "available", (mean("memfree") / mean("memtotal") * 100) AS "free" FROM "memory" WHERE ("sensu_entity_name" = \'$entity\') AND $timeFilter GROUP BY time($__interval) fill(linear)',
      '$col',
    )
  ),
  {x: 0, y: 0, w: 12, h: 10},
).addPanel(
  grafana.graphPanel.new(
    'Network traffic',
    datasource='$INFLUX_DS',
    legend_show=false,
  ).addTarget(
    grafana.influxdb.target(
      'SELECT difference(max(/eth0.*bytes/)) FROM "net" WHERE ("sensu_entity_name" = \'$entity\') AND $timeFilter GROUP BY time($__interval) fill(none)',
    )
  ),
  {x: 12, y: 0, w: 12, h: 10},
).addPanel(
  grafana.graphPanel.new(
    'CPU statistics',
    datasource='$INFLUX_DS',
    legend_show=false,
    stack=true,
    percentage=true,
    min=0,
    max=100,
    lines=false,
    bars=true,
  ).addTarget(
    grafana.influxdb.target(
      'SELECT difference(mean(*)) FROM "cpu" WHERE ("sensu_entity_name" = \'$entity\') AND $timeFilter GROUP BY time($__interval) fill(none)',
    )
  ),
  {x: 0, y: 10, w: 12, h: 10},
).addPanel(
  grafana.graphPanel.new(
    'Processes',
    datasource='$INFLUX_DS',
  ).addTarget(
    grafana.influxdb.target(
      'SELECT mean("value") FROM /procs_.*/ WHERE ("sensu_entity_name" = \'$entity\') AND $timeFilter GROUP BY time($__interval) fill(none)',
    )
  ),
  {x: 12, y: 10, w: 12, h: 10},
).addPanel(
  grafana.graphPanel.new(
    'Disks',
    datasource='$INFLUX_DS',
  ).addTarget(
    grafana.influxdb.target(
      'SELECT max("pct_used") FROM disk_usage WHERE ("sensu_entity_name" = \'$entity\') AND $timeFilter GROUP BY time($__interval), mountpoint fill(none)',
      '$tag_mountpoint',
    )
  ),
  {x: 0, y: 20, w: 12, h: 10},
)
