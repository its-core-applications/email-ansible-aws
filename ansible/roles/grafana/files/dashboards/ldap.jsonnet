local grafana = import 'grafonnet/grafana.libsonnet';

local regions = std.extVar('regions');

local regionTargets(query) = [
  grafana.influxdb.target(
    query,
    region,
    region + ' InfluxDB',
  )
  for region in regions
];

local regionQueryPanel(
  name,
  query,
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
  regionTargets(query)
);

local gridPos(x, y) = {
  x: x * 12,
  y: y * 7,
  w: 12,
  h: 7,
};

grafana.dashboard.new(
  'LDAP',
  schemaVersion=16,
  uid='ldap',
  time_from='now-3h',
  refresh='5s',
).addPanel(
  regionQueryPanel(
    'Connection Error',
    max=30,
    decimals=1,
    query='SELECT sum("ldap.connection.error.value") FROM "simta" WHERE $timeFilter GROUP BY time($__interval) fill(null)',
  ),
  gridPos(0, 0),
).addPanel(
  regionQueryPanel(
    'Query Error',
    max=30,
    decimals=1,
    query='SELECT sum("ldap.query_result.error.value") FROM "simta" WHERE $timeFilter GROUP BY time($__interval) fill(null)',
  ),
  gridPos(1, 0),
).addPanel(
  regionQueryPanel(
    'Success',
    query='SELECT sum("ldap.query_result.success.value") FROM "simta" WHERE $timeFilter GROUP BY time($__interval) fill(null)',
  ),
  gridPos(0, 1),
).addPanel(
  regionQueryPanel(
    'Not Found',
    query='SELECT sum("ldap.query_result.success.value") FROM "simta" WHERE $timeFilter GROUP BY time($__interval) fill(null)',
  ),
  gridPos(1, 1),
)
