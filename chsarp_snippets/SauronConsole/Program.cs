using System;
using System.Threading.Tasks;
using Aristocrat.Diagnostics;
using Aristocrat.Sauron;

namespace SauronConsole
{
	class Program
	{
		static void Main(string[] args)
		{
			AppDomain.CurrentDomain.UnhandledException += Program.OnUnhandledException;

			using (var container = WindsorBootstrapper.Bootstrap())
			{
				var engines = container.ResolveAll<IEngine>();
				Parallel.ForEach(engines, (engine) => {
					engine.Open();
				});

				Console.WriteLine("Press <ENTER> to exit...");
				Console.ReadLine();
			}// using
		}

		private static void OnUnhandledException(object sender, UnhandledExceptionEventArgs e)
		{
			SourceTrace.TraceCritical(SauronTrace.Source,
				@"An unhandled exception was thrown",
				new TraceCollection {
					{ "Exception", e.ExceptionObject }
				});
		}
	}
}
