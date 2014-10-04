#include "RoleFactory.h"
using namespace std;

BaseRoleFactoryItem::BaseRoleFactoryItem(const string &name)
{
    RoleFactory::singleton().add_role(name, this);
}

RoleFactory& RoleFactory::singleton()
{
    static RoleFactory* fact = new RoleFactory();
    return *fact;
}

// add_role adds a factory for role of type 'name'
// It is called automatically when instantiating a new RoleFactoryItem.
void RoleFactory::add_role(const string &name, BaseRoleFactoryItem *factory)
{
    m_factories[name] = factory;
}

// instantiate_role creates a new Role object of type 'role_name'.
Role* RoleFactory::instantiate_role(const string &role_name, RoleConfig roleconfig)
{
    if(m_factories.find(role_name) != m_factories.end()) {
        return m_factories[role_name]->instantiate(roleconfig);
    }
    return nullptr;
}
