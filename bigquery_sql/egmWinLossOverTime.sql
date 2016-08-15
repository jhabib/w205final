SELECT
  egmId,
  dateTime,
  ROUND(FLOAT(finalWager * denom * RAND(7) / (100000 * 1000)), 2) AS wager,
  ROUND(FLOAT(finalWin * denom * RAND(23) / (100000 * 1000)), 2) AS win
FROM (
  SELECT
    _id,
    REGEXP_EXTRACT(Key, r'([^-]*)') AS egmId,
    TIMESTAMP(REPLACE(LEFT(REGEXP_REPLACE(JSON_EXTRACT(Value, '$.eventDateTime'), r'([TZ])', ' '), 20), '"', '')) AS dateTime,
    INTEGER(JSON_EXTRACT(Value, '$.transactionList.transactionInfo[0].Item.finalWager')) AS finalWager,
    INTEGER(JSON_EXTRACT(Value, '$.transactionList.transactionInfo[0].Item.finalWin')) AS finalWin, 
    INTEGER(JSON_EXTRACT(Value, '$.transactionList.transactionInfo[0].Item.denomId')) AS denom
  FROM (
    SELECT
      *
    FROM
      [sauron.events]
    WHERE
      REGEXP_EXTRACT(Key, r'-([^-]+)-') == 'G2S_GPE111' ) )
ORDER BY
  egmId, dateTime
