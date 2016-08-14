using Castle.MicroKernel.Resolvers.SpecializedResolvers;
using Castle.Windsor;
using Castle.Windsor.Installer;

namespace SauronConsole
{
	internal static class WindsorBootstrapper
	{
		#region public methods

		public static IWindsorContainer Bootstrap()
		{
			var container = new WindsorContainer();
			container.Kernel.Resolver.AddSubResolver(new CollectionResolver(container.Kernel));

			container.Install(Configuration.FromAppConfig(),
				FromAssembly.InThisApplication());

			return container;
		}

		#endregion // constructors
	}
}
