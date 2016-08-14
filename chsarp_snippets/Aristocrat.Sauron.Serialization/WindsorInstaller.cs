using Castle.MicroKernel.Registration;
using Castle.MicroKernel.SubSystems.Configuration;
using Castle.Windsor;

namespace Aristocrat.Sauron.Serialization
{
	/// <summary>
	/// 
	/// </summary>
	/// <seealso cref="Castle.MicroKernel.Registration.IWindsorInstaller" />
	public class WindsorInstaller : IWindsorInstaller
	{
		#region public methods

		/// <summary>
		///   Performs the installation in the <see cref="T:Castle.Windsor.IWindsorContainer" />.
		/// </summary>
		/// <param name="container">The container.</param>
		/// <param name="store">The configuration store.</param>
		public void Install(IWindsorContainer container, IConfigurationStore store)
		{
			container.Register(Classes.FromThisAssembly()
				.BasedOn<ISerializer>()
				.WithServiceAllInterfaces()
				.Configure(component => component.LifestyleSingleton()));

			//.Configure(component => component.Named(component.Implementation);
			container.Register(Component.For<IPublisher>()
				.ImplementedBy<MongoPublisher>());
		}

		#endregion // public methods
	}
}
