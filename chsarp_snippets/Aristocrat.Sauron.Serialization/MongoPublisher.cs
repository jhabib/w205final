using System;
using System.Configuration;
using Aristocrat.Diagnostics;
using MongoDB.Driver;

namespace Aristocrat.Sauron.Serialization
{
	/// <summary>
	/// 
	/// </summary>
	public class MongoPublisher : IPublisher
	{
		#region private fields

		private string _connection;

		#endregion // private fields

		#region constructors

		/// <summary>
		/// Initializes a new instance of the <see cref="Aristocrat.Sauron.Serialization.MongoPublisher"/> class.
		/// </summary>
		public MongoPublisher()
		{
			var settings = ConfigurationManager.ConnectionStrings[@"MongoDB"];
			if (settings != null)
				this._connection = settings.ConnectionString;

			var database = Client().GetDatabase("sauron");

			// setup the counters database
			var counters = database.GetCollection<Counter>("counter");
			counters.Indexes.CreateOneAsync(Builders<Counter>.IndexKeys.Text(_ => _.Name),
				new CreateIndexOptions { Unique = true });

			// setup the event database
			var events = database.GetCollection<AnalyticInfo>("event");
			events.Indexes.CreateOneAsync(Builders<AnalyticInfo>.IndexKeys.Text(_ => _._id),
				new CreateIndexOptions { Unique = true });

			// setup the profile database
			var profile = database.GetCollection<AnalyticInfo>("profile");
			profile.Indexes.CreateOneAsync(Builders<AnalyticInfo>.IndexKeys.Text(_ => _._id),
				new CreateIndexOptions { Unique = true });
		}

		#endregion // constructors

		#region public methods

		/// <summary>
		/// Publishes the specified information.
		/// </summary>
		/// <param name="topic">The topic.</param>
		/// <param name="key">The key.</param>
		/// <param name="info">The serialized information.</param>
		public void Publish(string topic, string key, object info)
		{
			if (string.IsNullOrEmpty(topic))
				throw new ArgumentNullException("topic");

			if (string.IsNullOrEmpty(key))
				throw new ArgumentNullException("key");

			var database = Client().GetDatabase("sauron");
			var index = database.IncrementCounter(topic + "Upload");
			var document = new AnalyticInfo {
				_id = index.Result,
				Topic = topic,
				Key = key,
				Value = this.Serializer.Serialize(info)
			};

			SourceTrace.TraceVerbose(SauronTrace.Source,
				"Data being published.",
				new TraceCollection {
					{ "Topic", topic },
					{ "_id", document._id },
					{ "Key", key },
					{ "Value", document.Value }
				});

			var collection = database.GetCollection<AnalyticInfo>(topic);
			collection.InsertOneAsync(document);
		}

		#endregion // public methods

		#region private methods

		private IMongoClient Client()
		{
			return this._connection == null ? new MongoClient() : new MongoClient(this._connection);
		}

		#endregion // private methods

		#region public properties

		/// <summary>
		/// Gets or sets the serializer.
		/// </summary>
		/// <value>The serializer.</value>
		public ISerializer Serializer
		{ get; set; }

		#endregion // public properties
	}
}
