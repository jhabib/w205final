SELECT
  egmId, wagerCategory, 
  COUNT(wagerCategory) AS wagerCategoryCounts
FROM (
  SELECT
    _id,
    REGEXP_EXTRACT(Key, r'([^-]*)') AS egmId, 
    JSON_EXTRACT(Value, '$.meterList.meterInfo[1].wagerMeters[0].wagerCategory') AS wagerCategory
  FROM (
    SELECT
      *
    FROM
      [sauron.events]
    WHERE
      REGEXP_EXTRACT(Key, r'-([^-]+)-') == 'G2S_GPE103' ))
      GROUP BY egmId, wagerCategory
ORDER BY
  egmId
