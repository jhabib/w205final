using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using MongoDB.Bson.Serialization.Attributes;

namespace Aristocrat.Sauron.Serialization
{
	/// <summary>
	/// 
	/// </summary>
	public class AnalyticInfo : IInfo
	{
		/// <summary>
		/// Gets or sets the topic.
		/// </summary>
		/// <value>The topic.</value>
		public string Topic
		{ get; set; }

		/// <summary>
		/// Gets or sets the identifier of the EGM.
		/// </summary>
		/// <value>The identifier of the EGM.</value>
		public string Key
		{ get; set; }

		/// <summary>
		/// Gets or sets the value.
		/// </summary>
		/// <value>The value.</value>
		public string Value
		{ get; set; }

		/// <summary>
		/// Gets or sets the index.
		/// </summary>
		/// <value>The index.</value>
		[BsonId]
		public long _id
		{ get; set; }

	}
}
