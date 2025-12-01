import React, { useState, useEffect } from 'react';
import '../styles/AdminDashboard.css';

const AdminDashboard = () => {
  // State for modals
  const [showQuickActions, setShowQuickActions] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  
  // Mock data - in a real app this would come from props or API
  const [stats, setStats] = useState({
    users: 1242,
    providers: 328,
    orders: 892,
    revenue: 24560
  });
  
  const [recentActivities] = useState([
    {
      id: 1,
      title: 'Novo usuário registrado',
      description: 'João Silva se registrou como cliente',
      timestamp: '2023-06-15 14:30',
      icon: 'user-plus'
    },
    {
      id: 2,
      title: 'Pedido concluído',
      description: 'Serviço de encanamento finalizado com sucesso',
      timestamp: '2023-06-15 13:45',
      icon: 'check-circle'
    },
    {
      id: 3,
      title: 'Novo prestador aprovado',
      description: 'Maria Oliveira foi aprovada como eletricista',
      timestamp: '2023-06-15 12:15',
      icon: 'user-tie'
    }
  ]);

  // Animation for stats counting
  useEffect(() => {
    const countUpElements = document.querySelectorAll('.count-up');
    countUpElements.forEach(element => {
      const target = parseInt(element.getAttribute('data-target'));
      const duration = 2000;
      const increment = target / (duration / 16);
      let current = 0;
      
      const updateCount = () => {
        current += increment;
        if (current < target) {
          element.textContent = Math.floor(current);
          requestAnimationFrame(updateCount);
        } else {
          element.textContent = target.toLocaleString();
        }
      };
      
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            updateCount();
            observer.unobserve(element);
          }
        });
      }, { threshold: 0.5 });
      
      observer.observe(element);
    });
  }, []);

  // Handle refresh
  const handleRefresh = () => {
    const btn = document.getElementById('refreshButton');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-3"></i> Atualizando...';
    btn.disabled = true;
    
    // Simulate refresh
    setTimeout(() => {
      btn.innerHTML = originalText;
      btn.disabled = false;
      alert('Dashboard atualizado com sucesso!');
    }, 1500);
  };

  // Quick actions data
  const quickActions = [
    {
      title: 'Histórico de Perfis',
      description: 'Visualizar alterações em perfis de usuários',
      icon: 'history',
      color: 'bg-yellow-100 text-yellow-600',
      bgColor: 'from-yellow-50 to-blue-50'
    },
    {
      title: 'Gerenciar Prestadores',
      description: 'Visualizar e gerenciar todos os prestadores de serviço',
      icon: 'user-tie',
      color: 'bg-blue-100 text-blue-600',
      bgColor: 'from-blue-50 to-purple-50'
    },
    {
      title: 'Gerenciar Pedidos',
      description: 'Visualizar e gerenciar todos os pedidos do sistema',
      icon: 'shopping-cart',
      color: 'bg-green-100 text-green-600',
      bgColor: 'from-green-50 to-blue-50'
    },
    {
      title: 'Gerenciar Serviços',
      description: 'Visualizar e gerenciar todos os serviços disponíveis',
      icon: 'concierge-bell',
      color: 'bg-cyan-100 text-cyan-600',
      bgColor: 'from-cyan-50 to-blue-50'
    },
    {
      title: 'Gerenciar Usuários',
      description: 'Visualizar e gerenciar todos os usuários do sistema',
      icon: 'users',
      color: 'bg-yellow-100 text-yellow-600',
      bgColor: 'from-yellow-50 to-blue-50'
    },
    {
      title: 'Gerenciar Patrocinadores',
      description: 'Visualizar e gerenciar todos os patrocinadores',
      icon: 'handshake',
      color: 'bg-red-100 text-red-600',
      bgColor: 'from-red-50 to-blue-50'
    },
    {
      title: 'Django Admin',
      description: 'Acesso completo ao painel administrativo do Django',
      icon: 'database',
      color: 'bg-gray-100 text-gray-600',
      bgColor: 'from-gray-50 to-blue-50'
    }
  ];

  // Toggle dark mode
  const toggleDarkMode = () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-10 dark:bg-gray-900">
      {/* Main Container */}
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-10">
        
        {/* Header Section */}
        <div className="bg-gradient-to-r from-purple-600 to-indigo-700 rounded-3xl p-8 md:p-10 mb-10 shadow-xl hover:shadow-2xl transition-shadow duration-300 dark:from-purple-800 dark:to-indigo-900">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-8">
            <div className="flex-1">
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">Painel Administrativo</h1>
              <p className="text-purple-100 text-xl">Visão geral do sistema e gerenciamento completo</p>
            </div>
            <div className="flex flex-wrap gap-4">
              <button 
                id="refreshButton"
                onClick={handleRefresh}
                className="bg-white bg-opacity-20 hover:bg-opacity-30 text-white font-semibold py-3 px-6 rounded-full transition-all duration-300 transform hover:-translate-y-1 flex items-center shadow-lg"
              >
                <i className="fas fa-sync-alt mr-3"></i> Atualizar
              </button>
              <button 
                onClick={() => setShowSettings(true)}
                className="bg-white bg-opacity-20 hover:bg-opacity-30 text-white font-semibold py-3 px-6 rounded-full transition-all duration-300 transform hover:-translate-y-1 flex items-center shadow-lg"
              >
                <i className="fas fa-cog mr-3"></i> Configurações
              </button>
              <button 
                onClick={() => setShowQuickActions(true)}
                className="bg-green-500 hover:bg-green-600 text-white font-semibold py-3 px-6 rounded-full transition-all duration-300 transform hover:-translate-y-1 flex items-center shadow-lg"
              >
                <i className="fas fa-bolt mr-3"></i> Ações Rápidas
              </button>
            </div>
          </div>
        </div>
        
        {/* Stats Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-10">
          <div className="bg-white rounded-3xl shadow-lg hover:shadow-xl transition-all duration-300 p-8 border border-gray-100 hover:-translate-y-2 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-750">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h5 className="text-gray-500 text-base font-medium mb-3 dark:text-gray-400">Total de Usuários</h5>
                <h2 className="text-4xl font-bold text-purple-600 mb-4 count-up dark:text-purple-400" data-target={stats.users}>0</h2>
                <div className="flex items-center text-green-500 text-base dark:text-green-400">
                  <i className="fas fa-arrow-up mr-2"></i>
                  <span>12% desde o mês passado</span>
                </div>
              </div>
              <div className="bg-purple-100 p-4 rounded-full dark:bg-purple-900/50">
                <i className="fas fa-users text-purple-600 text-2xl dark:text-purple-400"></i>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-3xl shadow-lg hover:shadow-xl transition-all duration-300 p-8 border border-gray-100 hover:-translate-y-2 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-750">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h5 className="text-gray-500 text-base font-medium mb-3 dark:text-gray-400">Prestadores</h5>
                <h2 className="text-4xl font-bold text-green-500 mb-4 count-up dark:text-green-400" data-target={stats.providers}>0</h2>
                <div className="flex items-center text-green-500 text-base dark:text-green-400">
                  <i className="fas fa-arrow-up mr-2"></i>
                  <span>8% desde o mês passado</span>
                </div>
              </div>
              <div className="bg-green-100 p-4 rounded-full dark:bg-green-900/50">
                <i className="fas fa-user-tie text-green-500 text-2xl dark:text-green-400"></i>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-3xl shadow-lg hover:shadow-xl transition-all duration-300 p-8 border border-gray-100 hover:-translate-y-2 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-750">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h5 className="text-gray-500 text-base font-medium mb-3 dark:text-gray-400">Pedidos</h5>
                <h2 className="text-4xl font-bold text-cyan-500 mb-4 count-up dark:text-cyan-400" data-target={stats.orders}>0</h2>
                <div className="flex items-center text-red-500 text-base dark:text-red-400">
                  <i className="fas fa-arrow-down mr-2"></i>
                  <span>2% desde o mês passado</span>
                </div>
              </div>
              <div className="bg-cyan-100 p-4 rounded-full dark:bg-cyan-900/50">
                <i className="fas fa-shopping-cart text-cyan-500 text-2xl dark:text-cyan-400"></i>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-3xl shadow-lg hover:shadow-xl transition-all duration-300 p-8 border border-gray-100 hover:-translate-y-2 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-750">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h5 className="text-gray-500 text-base font-medium mb-3 dark:text-gray-400">Receita Total</h5>
                <h2 className="text-4xl font-bold text-yellow-500 mb-4 dark:text-yellow-400">R$ <span className="count-up" data-target={stats.revenue}>0</span></h2>
                <div className="flex items-center text-green-500 text-base dark:text-green-400">
                  <i className="fas fa-arrow-up mr-2"></i>
                  <span>15% desde o mês passado</span>
                </div>
              </div>
              <div className="bg-yellow-100 p-4 rounded-full dark:bg-yellow-900/50">
                <i className="fas fa-dollar-sign text-yellow-500 text-2xl dark:text-yellow-400"></i>
              </div>
            </div>
          </div>
        </div>
        
        {/* System Health and Activity Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
          {/* System Health Card */}
          <div className="bg-white rounded-3xl shadow-lg border border-gray-100 overflow-hidden dark:bg-gray-800 dark:border-gray-700">
            <div className="border-b border-gray-200 py-6 px-8 dark:border-gray-700">
              <div className="flex justify-between items-center">
                <h5 className="font-bold text-purple-600 flex items-center text-xl dark:text-purple-400">
                  <i className="fas fa-heartbeat mr-4"></i>
                  <span>Saúde do Sistema</span>
                </h5>
                <span className="bg-green-100 text-green-800 text-base font-medium px-5 py-3 rounded-full flex items-center dark:bg-green-900/50 dark:text-green-400">
                  <i className="fas fa-check-circle mr-2"></i> Operando Normalmente
                </span>
              </div>
            </div>
            <div className="p-8">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="bg-green-50 rounded-2xl p-6 text-center transition-all duration-300 hover:shadow-md hover:-translate-y-1 dark:bg-green-900/30 dark:hover:bg-green-900/50">
                  <div className="bg-green-100 w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-4 dark:bg-green-900/50">
                    <i className="fas fa-server text-green-600 text-2xl dark:text-green-400"></i>
                  </div>
                  <div className="text-3xl font-bold text-green-600 mb-2 dark:text-green-400">99.9%</div>
                  <div className="text-gray-600 text-base dark:text-gray-400">Uptime</div>
                </div>
                
                <div className="bg-blue-50 rounded-2xl p-6 text-center transition-all duration-300 hover:shadow-md hover:-translate-y-1 dark:bg-blue-900/30 dark:hover:bg-blue-900/50">
                  <div className="bg-blue-100 w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-4 dark:bg-blue-900/50">
                    <i className="fas fa-tachometer-alt text-blue-600 text-2xl dark:text-blue-400"></i>
                  </div>
                  <div className="text-3xl font-bold text-blue-600 mb-2 dark:text-blue-400">120ms</div>
                  <div className="text-gray-600 text-base dark:text-gray-400">Latência</div>
                </div>
                
                <div className="bg-yellow-50 rounded-2xl p-6 text-center transition-all duration-300 hover:shadow-md hover:-translate-y-1 dark:bg-yellow-900/30 dark:hover:bg-yellow-900/50">
                  <div className="bg-yellow-100 w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-4 dark:bg-yellow-900/50">
                    <i className="fas fa-database text-yellow-600 text-2xl dark:text-yellow-400"></i>
                  </div>
                  <div className="text-3xl font-bold text-yellow-600 mb-2 dark:text-yellow-400">85%</div>
                  <div className="text-gray-600 text-base dark:text-gray-400">Armazenamento</div>
                </div>
                
                <div className="bg-red-50 rounded-2xl p-6 text-center transition-all duration-300 hover:shadow-md hover:-translate-y-1 dark:bg-red-900/30 dark:hover:bg-red-900/50">
                  <div className="bg-red-100 w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-4 dark:bg-red-900/50">
                    <i className="fas fa-exclamation-triangle text-red-600 text-2xl dark:text-red-400"></i>
                  </div>
                  <div className="text-3xl font-bold text-red-600 mb-2 dark:text-red-400">0</div>
                  <div className="text-gray-600 text-base dark:text-gray-400">Erros</div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Recent Activity Card */}
          <div className="bg-white rounded-3xl shadow-lg border border-gray-100 dark:bg-gray-800 dark:border-gray-700">
            <div className="border-b border-gray-200 py-6 px-8 dark:border-gray-700">
              <h5 className="font-bold text-purple-600 flex items-center text-xl dark:text-purple-400">
                <i className="fas fa-history mr-4"></i>
                <span>Atividade Recente</span>
              </h5>
            </div>
            <div className="p-8">
              {recentActivities.length > 0 ? (
                <div className="space-y-8">
                  {recentActivities.map(activity => (
                    <div key={activity.id} className="flex group">
                      <div className="mr-6">
                        <div className="bg-purple-600 rounded-full w-12 h-12 flex items-center justify-center dark:bg-purple-700">
                          <i className={`fas fa-${activity.icon} text-white text-lg`}></i>
                        </div>
                      </div>
                      <div className="flex-1 pb-8 last:pb-0">
                        <h6 className="font-bold text-gray-800 text-lg mb-2 dark:text-gray-200">{activity.title}</h6>
                        <p className="text-gray-600 mb-3 dark:text-gray-400">{activity.description}</p>
                        <small className="text-gray-500 text-base dark:text-gray-500">{activity.timestamp}</small>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <i className="fas fa-history text-gray-300 text-5xl mb-5 dark:text-gray-600"></i>
                  <h6 className="text-gray-700 font-medium text-xl mb-3 dark:text-gray-300">Nenhuma atividade recente</h6>
                  <p className="text-gray-500 text-lg dark:text-gray-500">Aqui aparecerão as atividades recentes do sistema</p>
                </div>
              )}
            </div>
          </div>
        </div>
        
        {/* System Statistics Card */}
        <div className="bg-white rounded-3xl shadow-lg border border-gray-100 mb-10 dark:bg-gray-800 dark:border-gray-700">
          <div className="border-b border-gray-200 py-6 px-8 dark:border-gray-700">
            <h5 className="font-bold text-purple-600 flex items-center text-xl dark:text-purple-400">
              <i className="fas fa-chart-pie mr-4"></i>
              <span>Estatísticas do Sistema</span>
            </h5>
          </div>
          <div className="p-8">
            <div className="mb-10">
              <div className="flex justify-between mb-4">
                <span className="font-bold text-gray-700 text-lg dark:text-gray-300">Usuários por Tipo</span>
                <span className="text-gray-500 text-lg dark:text-gray-500">Total: {stats.users.toLocaleString()}</span>
              </div>
              <div className="h-4 bg-gray-200 rounded-full mb-4 overflow-hidden dark:bg-gray-700">
                <div className="h-full flex">
                  <div className="bg-purple-600" style={{ width: '60%' }}></div>
                  <div className="bg-green-500" style={{ width: '25%' }}></div>
                  <div className="bg-cyan-500" style={{ width: '15%' }}></div>
                </div>
              </div>
              <div className="flex justify-between text-base text-gray-500 dark:text-gray-500">
                <span>Clientes (60%)</span>
                <span>Prestadores (25%)</span>
                <span>Admins (15%)</span>
              </div>
            </div>
            
            <div className="mb-10">
              <div className="flex justify-between mb-4">
                <span className="font-bold text-gray-700 text-lg dark:text-gray-300">Pedidos por Status</span>
                <span className="text-gray-500 text-lg dark:text-gray-500">Total: {stats.orders.toLocaleString()}</span>
              </div>
              <div className="h-4 bg-gray-200 rounded-full mb-4 overflow-hidden dark:bg-gray-700">
                <div className="h-full flex">
                  <div className="bg-green-500" style={{ width: '40%' }}></div>
                  <div className="bg-yellow-500" style={{ width: '30%' }}></div>
                  <div className="bg-cyan-500" style={{ width: '20%' }}></div>
                  <div className="bg-gray-500" style={{ width: '10%' }}></div>
                </div>
              </div>
              <div className="flex justify-between text-base text-gray-500 dark:text-gray-500">
                <span>Concluídos (40%)</span>
                <span>Pendentes (30%)</span>
                <span>Em Andamento (20%)</span>
                <span>Cancelados (10%)</span>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between mb-4">
                <span className="font-bold text-gray-700 text-lg dark:text-gray-300">Receita por Categoria</span>
                <span className="text-gray-500 text-lg dark:text-gray-500">Total: R$ {stats.revenue.toLocaleString()}</span>
              </div>
              <div className="h-4 bg-gray-200 rounded-full mb-4 overflow-hidden dark:bg-gray-700">
                <div className="h-full flex">
                  <div className="bg-purple-600" style={{ width: '30%' }}></div>
                  <div className="bg-green-500" style={{ width: '25%' }}></div>
                  <div className="bg-yellow-500" style={{ width: '20%' }}></div>
                  <div className="bg-cyan-500" style={{ width: '15%' }}></div>
                  <div className="bg-red-500" style={{ width: '10%' }}></div>
                </div>
              </div>
              <div className="flex justify-between text-base text-gray-500 dark:text-gray-500">
                <span>Reparos (30%)</span>
                <span>Montagem (25%)</span>
                <span>Encanamento (20%)</span>
                <span>Elétrica (15%)</span>
                <span>Outros (10%)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Quick Actions Modal */}
      {showQuickActions && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-6">
          <div className="bg-white rounded-3xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-y-auto dark:bg-gray-800">
            <div className="border-b border-gray-200 py-6 px-8 flex justify-between items-center dark:border-gray-700">
              <h5 className="font-bold text-purple-600 text-2xl dark:text-purple-400">Ações Rápidas</h5>
              <button 
                onClick={() => setShowQuickActions(false)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
              >
                <i className="fas fa-times text-2xl"></i>
              </button>
            </div>
            <div className="p-8">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {quickActions.map((action, index) => (
                  <div 
                    key={index}
                    className="bg-gradient-to-br rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:-translate-y-1 border border-gray-100 dark:border-gray-700 dark:hover:border-gray-600"
                  >
                    <div className="text-center">
                      <div className={`${action.color} w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-5 dark:bg-opacity-20`}>
                        <i className={`fas fa-${action.icon} text-3xl`}></i>
                      </div>
                      <h6 className="font-bold text-gray-800 text-xl mb-3 dark:text-gray-200">{action.title}</h6>
                      <p className="text-gray-600 text-base dark:text-gray-400">{action.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="border-t border-gray-200 py-5 px-8 flex justify-end dark:border-gray-700">
              <button 
                onClick={() => setShowQuickActions(false)}
                className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-3 px-7 rounded-full transition-colors duration-300 text-lg dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-gray-200"
              >
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Settings Modal */}
      {showSettings && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-6">
          <div className="bg-white rounded-3xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto dark:bg-gray-800">
            <div className="border-b border-gray-200 py-6 px-8 flex justify-between items-center dark:border-gray-700">
              <h5 className="font-bold text-purple-600 text-2xl dark:text-purple-400">Configurações</h5>
              <button 
                onClick={() => setShowSettings(false)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
              >
                <i className="fas fa-times text-2xl"></i>
              </button>
            </div>
            <div className="p-8">
              <div className="mb-10">
                <h6 className="font-bold text-purple-600 mb-5 text-xl dark:text-purple-400">Personalização</h6>
                <div className="bg-gray-50 rounded-2xl p-6 mb-5 flex justify-between items-center dark:bg-gray-700">
                  <div>
                    <div className="font-bold text-gray-800 text-lg mb-2 dark:text-gray-200">Modo Escuro</div>
                    <div className="text-gray-600 text-base dark:text-gray-400">Ativar tema escuro para o painel</div>
                  </div>
                  <div className="relative inline-block w-14 h-7">
                    <input type="checkbox" className="opacity-0 w-0 h-0 peer" id="darkModeToggle" onChange={toggleDarkMode} />
                    <label 
                      htmlFor="darkModeToggle" 
                      className="absolute cursor-pointer top-0 left-0 right-0 bottom-0 bg-gray-300 rounded-full transition duration-300 before:absolute before:h-5 before:w-5 before:left-1 before:bottom-1 before:bg-white before:rounded-full before:transition before:duration-300 peer-checked:bg-purple-600 peer-checked:before:translate-x-7 dark:bg-gray-600 dark:before:bg-gray-300"
                    ></label>
                  </div>
                </div>
              </div>
              
              <div className="mb-10">
                <h6 className="font-bold text-purple-600 mb-5 text-xl dark:text-purple-400">Notificações</h6>
                <div className="bg-gray-50 rounded-2xl p-6 mb-5 flex justify-between items-center dark:bg-gray-700">
                  <div>
                    <div className="font-bold text-gray-800 text-lg mb-2 dark:text-gray-200">Email</div>
                    <div className="text-gray-600 text-base dark:text-gray-400">Receber notificações por email</div>
                  </div>
                  <div className="relative inline-block w-14 h-7">
                    <input type="checkbox" className="opacity-0 w-0 h-0 peer" id="emailNotifications" defaultChecked />
                    <label 
                      htmlFor="emailNotifications" 
                      className="absolute cursor-pointer top-0 left-0 right-0 bottom-0 bg-gray-300 rounded-full transition duration-300 before:absolute before:h-5 before:w-5 before:left-1 before:bottom-1 before:bg-white before:rounded-full before:transition before:duration-300 peer-checked:bg-purple-600 peer-checked:before:translate-x-7 dark:bg-gray-600 dark:before:bg-gray-300"
                    ></label>
                  </div>
                </div>
                
                <div className="bg-gray-50 rounded-2xl p-6 flex justify-between items-center dark:bg-gray-700">
                  <div>
                    <div className="font-bold text-gray-800 text-lg mb-2 dark:text-gray-200">Push</div>
                    <div className="text-gray-600 text-base dark:text-gray-400">Receber notificações push</div>
                  </div>
                  <div className="relative inline-block w-14 h-7">
                    <input type="checkbox" className="opacity-0 w-0 h-0 peer" id="pushNotifications" />
                    <label 
                      htmlFor="pushNotifications" 
                      className="absolute cursor-pointer top-0 left-0 right-0 bottom-0 bg-gray-300 rounded-full transition duration-300 before:absolute before:h-5 before:w-5 before:left-1 before:bottom-1 before:bg-white before:rounded-full before:transition before:duration-300 peer-checked:bg-purple-600 peer-checked:before:translate-x-7 dark:bg-gray-600 dark:before:bg-gray-300"
                    ></label>
                  </div>
                </div>
              </div>
              
              <div>
                <h6 className="font-bold text-purple-600 mb-5 text-xl dark:text-purple-400">Idioma</h6>
                <select className="w-full bg-gray-50 border border-gray-300 text-gray-900 rounded-full py-4 px-5 focus:ring-purple-500 focus:border-purple-500 text-lg dark:bg-gray-700 dark:border-gray-600 dark:text-gray-200">
                  <option>Português (Brasil)</option>
                  <option>English</option>
                  <option>Español</option>
                </select>
              </div>
            </div>
            <div className="border-t border-gray-200 py-5 px-8 flex justify-end space-x-4 dark:border-gray-700">
              <button 
                onClick={() => setShowSettings(false)}
                className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-3 px-7 rounded-full transition-colors duration-300 text-lg dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-gray-200"
              >
                Fechar
              </button>
              <button className="bg-purple-600 hover:bg-purple-700 text-white font-medium py-3 px-7 rounded-full transition-colors duration-300 text-lg dark:bg-purple-700 dark:hover:bg-purple-600">
                Salvar Alterações
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;