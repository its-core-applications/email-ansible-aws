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
  ) for region in regions
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

local gridPos(x, y) = {
  x: x * 12,
  y: y * 7,
  w: 12,
  h: 7,
};

grafana.dashboard.new(
  'Mail Overview',
  schemaVersion=16,
  uid='mail-overview',
  time_from='now-3h',
  refresh='5s',
).addAnnotations(
  [
    grafana.annotation.datasource(
      region + ' plasticman scale events',
      region + ' InfluxDB'
    ) {
      query: "SELECT * FROM plasticman WHERE phase = 'end'",
      textColumn: 'action',
    } for region in regions
  ]
).addPanel(
  regionQueryPanel(
    'Average load average',
    max=20,
    decimals=1,
    query='SELECT mean("5_min") FROM "load_avg" WHERE $timeFilter GROUP BY time($__interval), "class" fill(linear)',
  ),
  gridPos(0, 0),
).addPanel(
  regionQueryPanel(
    'Open inbound SMTP connections',
    query='SELECT max("sum") FROM (SELECT sum("estab") FROM "simta_sockets" WHERE $timeFilter GROUP BY time(10s), "class") GROUP BY time($__interval), "class" fill(none)',
  ),
  gridPos(1, 0),
).addPanel(
  regionQueryPanel(
    'Large host queues',
    query='SELECT max("sum") FROM (SELECT sum("messages") FROM "simta_host_queue" WHERE $timeFilter AND "messages" > 50 GROUP BY time(10s), "remote_host", "class") GROUP BY time($__interval), "remote_host", "class" fill(none)',
    query_alias='$tag_class.$tag_remote_host'
  ),
  gridPos(0, 1),
).addPanel(
  regionQueryPanel(
    'Fast queues',
    query='SELECT max("sum") FROM (SELECT sum("fast") FROM "simta_queue" WHERE $timeFilter GROUP BY time(10s), "class") GROUP BY time($__interval), "class" fill(none)',
  ),
  gridPos(1, 1),
).addPanel(
  regionQueryPanel(
    'Host counts',
    query='SELECT max("sum") FROM (SELECT sum("instance_count") FROM "ec2" WHERE $timeFilter AND "Status" = \'production\' GROUP BY time(10s), "Class") GROUP BY time($__interval), "Class" fill(previous)',
    query_alias='$tag_Class',
  ),
  gridPos(0, 2),
).addPanel(
  regionQueryPanel(
    'Slow queues',
    query='SELECT max("sum") FROM (SELECT sum("slow") FROM "simta_queue" WHERE $timeFilter GROUP BY time(10s), "class") GROUP BY time($__interval), "class" fill(none)',
  ),
  gridPos(1, 2),
)
