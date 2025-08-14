local grafana = import 'grafonnet/grafana.libsonnet';

local regions = std.extVar('regions');

local regionTargets(
  query,
  alias=null,
      ) = [
  grafana.influxdb.target(
    query,
    if alias != null then region + '.' + alias,
    region + ' InfluxDB',
  )
  for region in regions
];

local regionQueryPanel(
  name,
  query,
  query_alias='$tag_class',
  min=0,
  max=null,
  decimals=0,
      ) = grafana.graphPanel.new(
  name,
  datasource='-- Mixed --',
  legend_show=false,
  min=min,
  max=max,
  decimals=decimals,
).addTargets(
  regionTargets(query, query_alias)
);

grafana.dashboard.new(
  'Mail Queue',
  schemaVersion=16,
  uid='mail-queue',
  time_from='now-3h',
  refresh='5s',
).addTemplate(
  grafana.template.new(
    'queue_host',
    regions[0] + ' InfluxDB',
    'SELECT DISTINCT("remote_host") FROM (SELECT "messages", "remote_host" FROM "simta_host_queue" WHERE $timeFilter)',
    refresh='time',
    sort=1,
  )
).addPanel(
  regionQueryPanel(
    'Queues',
    query='SELECT sum("messages") FROM "simta_host_queue" WHERE $timeFilter AND ("remote_host" = \'$queue_host\') GROUP BY time($__interval), "class" fill(none)',
  ),
  { x: 0, y: 0, w: 24, h: 20 }
)
