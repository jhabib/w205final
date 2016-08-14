using MongoDB.Bson.Serialization.Attributes;

namespace Aristocrat.Sauron.Serialization
{
	/// <summary>
	/// 
	/// </summary>
	public class Counter
	{
		/// <summary>
		/// Gets or sets the collection.
		/// </summary>
		/// <value>The collection.</value>
		[BsonId]
		public string Name
		{ get; set; }

		/// <summary>
		/// Gets or sets the sequence number.
		/// </summary>
		/// <value>The sequence number.</value>
		public long SequenceNumber
		{ get; set; }
	}
}
