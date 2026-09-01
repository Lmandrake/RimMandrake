using System.Text;
using System.Xml;
using System.Xml.Linq;

namespace VEF;

internal class GlobalSettingsUtilities
{
	public static string PrettyXml(string xml)
	{
		StringBuilder stringBuilder = new StringBuilder();
		XElement xElement = XElement.Parse(xml);
		XmlWriterSettings settings = new XmlWriterSettings
		{
			OmitXmlDeclaration = true,
			Indent = true,
			NewLineOnAttributes = false
		};
		using (XmlWriter writer = XmlWriter.Create(stringBuilder, settings))
		{
			xElement.Save(writer);
		}
		return stringBuilder.ToString();
	}
}
