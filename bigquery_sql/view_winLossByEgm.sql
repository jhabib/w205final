SELECT
  egmId,
  SUM(finalWager) AS totalBet,
  SUM(finalWin) AS totalWin,
  SUM(finalWin - finalWager) AS netWin,
  AVG(FLOAT(finalWin/finalWager)) AS winRatio
FROM (
  SELECT
    _id,
    REGEXP_EXTRACT(Key, r'([^-]*)') AS egmId,
    INTEGER(JSON_EXTRACT(Value, '$.transactionList.transactionInfo[0].Item.finalWager')) AS finalWager,
    INTEGER(JSON_EXTRACT(Value, '$.transactionList.transactionInfo[0].Item.finalWin')) AS finalWin
  FROM (
    SELECT
      *
    FROM
      [sauron.events]
    WHERE
      REGEXP_EXTRACT(Key, r'-([^-]+)-') == 'G2S_GPE111' ) )
GROUP BY
  egmId
ORDER BY
  egmId
