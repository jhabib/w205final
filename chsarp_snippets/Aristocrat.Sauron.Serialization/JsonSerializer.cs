using Newtonsoft.Json;

namespace Aristocrat.Sauron.Serialization
{
	/// <summary>
	/// 
	/// </summary>
	/// <seealso cref="Aristocrat.Sauron.ISerializer" />
	public class JsonSerializer : ISerializer
	{
		#region public methods

		/// <summary>
		/// Serializes the specified item.
		/// </summary>
		/// <param name="value">The object to serialize.</param>
		/// <returns><paramref name="value"/> serialized as a string.</returns>
		public string Serialize(object value)
		{
			return JsonConvert.SerializeObject(value, Formatting.Indented);
		}

		/// <summary>
		/// Deserializes the specified stream.
		/// </summary>
		/// <param name="value">The string to deserialize.</param>
		/// <returns>The deserialized object.</returns>
		public object Deserialize(string value)
		{
			return JsonConvert.DeserializeObject(value);
		}

		#endregion // public methods
	}
}
