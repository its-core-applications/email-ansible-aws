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

local gridPos(x, y) = {
  x: x * 24,
  y: y * 14,
  w: 24,
  h: 14,
};

grafana.dashboard.new(
  'SenderScore',
  schemaVersion=16,
  uid='senderscore',
  time_from='now-3h',
  refresh='5s',
).addPanel(
  regionQueryPanel(
    'Score',
    max=100,
    decimals=1,
    query='SELECT max("score") FROM "sender_score" WHERE $timeFilter GROUP BY time($__interval), "sensu_entity_name" fill(none)',
    query_alias='$tag_sensu_entity_name',
  ),
  gridPos(0, 0),
)
