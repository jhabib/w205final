using System;
using System.Threading.Tasks;
using MongoDB.Driver;

namespace Aristocrat.Sauron.Serialization
{
	internal static class MongoExtensions
	{
		public static async Task<long> IncrementCounter(this IMongoDatabase database, string counter)
		{
			if (database == null)
				throw new ArgumentNullException("database");

			var collection = database.GetCollection<Counter>("counter");

			var result = await collection.FindOneAndUpdateAsync(Builders<Counter>.Filter.Eq(_ => _.Name, counter),
				Builders<Counter>.Update
					.Inc(_ => _.SequenceNumber, 1),
					//.SetOnInsert(_ => _.SequenceNumber, 1),
				new FindOneAndUpdateOptions<Counter, Counter> {
					IsUpsert = true,
					ReturnDocument = ReturnDocument.After,
				});

			return result.SequenceNumber;
		}
	}
}
