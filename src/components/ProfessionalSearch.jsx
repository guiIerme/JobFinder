import React, { useState, useEffect } from 'react';

// Professional Search Component with Tailwind CSS
const ProfessionalSearch = () => {
  // State for filters
  const [filters, setFilters] = useState({
    search: '',
    location: '',
    category: '',
    rating: '',
    price: '',
    nearby: false
  });

  // State for professionals data
  const [professionals, setProfessionals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sortOption, setSortOption] = useState('rating');

  // Mock data for categories
  const categories = [
    { key: 'repair', name: 'Reparo', icon: '🔧' },
    { key: 'assembly', name: 'Montagem', icon: '🛠️' },
    { key: 'plumbing', name: 'Encanamento', icon: '🚰' },
    { key: 'electrical', name: 'Elétrica', icon: '⚡' },
    { key: 'cleaning', name: 'Limpeza', icon: '🧹' },
    { key: 'painting', name: 'Pintura', icon: '🎨' }
  ];

  // Mock data for professionals
  const mockProfessionals = [
    {
      id: 1,
      name: 'João Silva',
      rating: 4.8,
      reviewCount: 42,
      service: 'Serviço de Elétrica Residencial',
      description: 'Especialista em instalações elétricas residenciais com 10 anos de experiência.',
      price: 150.00,
      category: 'Elétrica',
      avatar: null
    },
    {
      id: 2,
      name: 'Maria Oliveira',
      rating: 4.9,
      reviewCount: 38,
      service: 'Montagem de Móveis',
      description: 'Montagem especializada de móveis de todos os tipos com garantia.',
      price: 80.00,
      category: 'Montagem',
      avatar: null
    },
    {
      id: 3,
      name: 'Carlos Santos',
      rating: 4.7,
      reviewCount: 56,
      service: 'Reparos Hidráulicos',
      description: 'Reparos rápidos e eficientes em encanamentos residenciais.',
      price: 120.00,
      category: 'Encanamento',
      avatar: null
    },
    {
      id: 4,
      name: 'Ana Costa',
      rating: 4.9,
      reviewCount: 29,
      service: 'Limpeza Pós-Obra',
      description: 'Limpeza especializada para imóveis após reformas e construções.',
      price: 200.00,
      category: 'Limpeza',
      avatar: null
    },
    {
      id: 5,
      name: 'Pedro Almeida',
      rating: 4.6,
      reviewCount: 45,
      service: 'Pintura Residencial',
      description: 'Pintura de alta qualidade para interiores e exteriores.',
      price: 180.00,
      category: 'Pintura',
      avatar: null
    },
    {
      id: 6,
      name: 'Fernanda Lima',
      rating: 4.8,
      reviewCount: 33,
      service: 'Reparos Gerais',
      description: 'Serviço completo de reparos e manutenção residencial.',
      price: 100.00,
      category: 'Reparo',
      avatar: null
    }
  ];

  // Initialize professionals data
  useEffect(() => {
    setProfessionals(mockProfessionals);
  }, []);

  // Handle filter changes
  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
  };

  // Apply filters
  const applyFilters = () => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      let filtered = [...mockProfessionals];
      
      // Apply search filter
      if (filters.search) {
        filtered = filtered.filter(professional => 
          professional.name.toLowerCase().includes(filters.search.toLowerCase()) ||
          professional.service.toLowerCase().includes(filters.search.toLowerCase()) ||
          professional.description.toLowerCase().includes(filters.search.toLowerCase())
        );
      }
      
      // Apply category filter
      if (filters.category) {
        filtered = filtered.filter(professional => 
          professional.category.toLowerCase() === filters.category.toLowerCase()
        );
      }
      
      // Apply rating filter
      if (filters.rating) {
        const minRating = parseInt(filters.rating);
        filtered = filtered.filter(professional => 
          professional.rating >= minRating
        );
      }
      
      // Apply price filter
      if (filters.price) {
        if (filters.price === '0-100') {
          filtered = filtered.filter(professional => professional.price <= 100);
        } else if (filters.price === '100-300') {
          filtered = filtered.filter(professional => 
            professional.price > 100 && professional.price <= 300
          );
        } else if (filters.price === '300+') {
          filtered = filtered.filter(professional => professional.price > 300);
        }
      }
      
      setProfessionals(filtered);
      setLoading(false);
    }, 500);
  };

  // Reset all filters
  const resetFilters = () => {
    setFilters({
      search: '',
      location: '',
      category: '',
      rating: '',
      price: '',
      nearby: false
    });
    setProfessionals(mockProfessionals);
  };

  // Handle sort change
  const handleSortChange = (value) => {
    setSortOption(value);
    // In a real app, this would trigger a new API call with sorting parameter
    let sorted = [...professionals];
    
    switch (value) {
      case 'rating':
        sorted.sort((a, b) => b.rating - a.rating);
        break;
      case 'price-low':
        sorted.sort((a, b) => a.price - b.price);
        break;
      case 'price-high':
        sorted.sort((a, b) => b.price - a.price);
        break;
      case 'newest':
        // For demo purposes, we'll just reverse the array
        sorted.reverse();
        break;
      default:
        break;
    }
    
    setProfessionals(sorted);
  };

  // Render star rating
  const renderStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    
    for (let i = 0; i < fullStars; i++) {
      stars.push(<span key={i} className="text-yellow-400">★</span>);
    }
    
    if (hasHalfStar) {
      stars.push(<span key="half" className="text-yellow-400">☆</span>);
    }
    
    const emptyStars = 5 - stars.length;
    for (let i = 0; i < emptyStars; i++) {
      stars.push(<span key={`empty-${i}`} className="text-gray-300">☆</span>);
    }
    
    return stars;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-700 rounded-2xl p-6 md:p-8 mb-8 shadow-lg hover:shadow-xl transition-shadow duration-300">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div className="flex items-center">
            <button 
              className="bg-white bg-opacity-20 hover:bg-opacity-30 rounded-full p-2 mr-4 transition-all duration-200"
              aria-label="Voltar para a página inicial"
            >
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-white">Buscar Profissionais</h1>
              <p className="text-white text-opacity-90 mt-1">
                {professionals.length} profissionais encontrados
              </p>
            </div>
          </div>
          
          <div className="flex items-center bg-white bg-opacity-20 rounded-full px-4 py-2">
            <span className="text-white font-medium mr-2">Ordenar por:</span>
            <select 
              className="bg-transparent text-white font-medium focus:outline-none"
              value={sortOption}
              onChange={(e) => handleSortChange(e.target.value)}
            >
              <option value="rating" className="text-gray-800">Melhor avaliados</option>
              <option value="price-low" className="text-gray-800">Menor preço</option>
              <option value="price-high" className="text-gray-800">Maior preço</option>
              <option value="newest" className="text-gray-800">Mais recentes</option>
            </select>
          </div>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Filters Sidebar */}
        <div className="lg:w-1/3">
          <div className="bg-white rounded-2xl shadow-lg p-6 sticky top-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-purple-700 flex items-center">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                </svg>
                Filtros
              </h2>
              <button 
                className="text-sm text-purple-600 hover:text-purple-800 font-medium"
                onClick={resetFilters}
              >
                Limpar
              </button>
            </div>

            {/* Search Filter */}
            <div className="mb-6">
              <h3 className="font-semibold text-gray-700 mb-3 flex items-center">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                Buscar
              </h3>
              <div className="flex">
                <input
                  type="text"
                  placeholder="Buscar profissionais..."
                  className="flex-1 border border-gray-300 rounded-l-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                />
                <button 
                  className="bg-purple-600 hover:bg-purple-700 text-white px-4 rounded-r-lg transition-colors duration-200"
                  onClick={applyFilters}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Location Filter */}
            <div className="mb-6">
              <h3 className="font-semibold text-gray-700 mb-3 flex items-center">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                Localização
              </h3>
              <div className="flex mb-3">
                <input
                  type="text"
                  placeholder="CEP ou cidade"
                  className="flex-1 border border-gray-300 rounded-l-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  value={filters.location}
                  onChange={(e) => handleFilterChange('location', e.target.value)}
                />
                <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 rounded-r-lg transition-colors duration-200">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  </svg>
                </button>
              </div>
              <div className="flex items-center justify-between bg-gray-100 rounded-lg p-3">
                <span className="text-gray-700">Próximos a mim</span>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input 
                    type="checkbox" 
                    className="sr-only peer"
                    checked={filters.nearby}
                    onChange={(e) => handleFilterChange('nearby', e.target.checked)}
                  />
                  <div className="w-11 h-6 bg-gray-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                </label>
              </div>
            </div>

            {/* Category Filter */}
            <div className="mb-6">
              <h3 className="font-semibold text-gray-700 mb-3 flex items-center">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                </svg>
                Categoria
              </h3>
              <div className="space-y-2">
                <label className="flex items-center p-3 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors duration-200">
                  <input
                    type="radio"
                    name="category"
                    className="h-4 w-4 text-purple-600 focus:ring-purple-500"
                    checked={filters.category === ''}
                    onChange={() => handleFilterChange('category', '')}
                  />
                  <span className="ml-3 text-gray-700">Todas as categorias</span>
                </label>
                {categories.map((category) => (
                  <label key={category.key} className="flex items-center p-3 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors duration-200">
                    <input
                      type="radio"
                      name="category"
                      className="h-4 w-4 text-purple-600 focus:ring-purple-500"
                      checked={filters.category === category.key}
                      onChange={() => handleFilterChange('category', category.key)}
                    />
                    <span className="ml-3 text-gray-700 flex items-center">
                      <span className="mr-2">{category.icon}</span>
                      {category.name}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Rating Filter */}
            <div className="mb-6">
              <h3 className="font-semibold text-gray-700 mb-3 flex items-center">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                </svg>
                Avaliação
              </h3>
              <div className="space-y-2">
                <label className="flex items-center p-3 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors duration-200">
                  <input
                    type="radio"
                    name="rating"
                    className="h-4 w-4 text-purple-600 focus:ring-purple-500"
                    checked={filters.rating === ''}
                    onChange={() => handleFilterChange('rating', '')}
                  />
                  <span className="ml-3 text-gray-700">Qualquer avaliação</span>
                </label>
                {[5, 4, 3].map((stars) => (
                  <label key={stars} className="flex items-center p-3 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors duration-200">
                    <input
                      type="radio"
                      name="rating"
                      className="h-4 w-4 text-purple-600 focus:ring-purple-500"
                      checked={filters.rating === String(stars)}
                      onChange={() => handleFilterChange('rating', String(stars))}
                    />
                    <span className="ml-3 text-gray-700 flex items-center">
                      {renderStars(stars)}
                      <span className="ml-2">{stars}+ estrelas</span>
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Price Range Filter */}
            <div className="mb-6">
              <h3 className="font-semibold text-gray-700 mb-3 flex items-center">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Faixa de Preço
              </h3>
              <div className="space-y-2">
                <label className="flex items-center p-3 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors duration-200">
                  <input
                    type="radio"
                    name="price"
                    className="h-4 w-4 text-purple-600 focus:ring-purple-500"
                    checked={filters.price === ''}
                    onChange={() => handleFilterChange('price', '')}
                  />
                  <span className="ml-3 text-gray-700">Qualquer preço</span>
                </label>
                {[
                  { value: '0-100', label: 'Até R$ 100' },
                  { value: '100-300', label: 'R$ 100 - R$ 300' },
                  { value: '300+', label: 'Acima de R$ 300' }
                ].map((priceOption) => (
                  <label key={priceOption.value} className="flex items-center p-3 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors duration-200">
                    <input
                      type="radio"
                      name="price"
                      className="h-4 w-4 text-purple-600 focus:ring-purple-500"
                      checked={filters.price === priceOption.value}
                      onChange={() => handleFilterChange('price', priceOption.value)}
                    />
                    <span className="ml-3 text-gray-700">{priceOption.label}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3">
              <button
                className="flex-1 bg-white border border-purple-600 text-purple-600 hover:bg-purple-50 rounded-lg py-2 px-4 font-medium transition-colors duration-200"
                onClick={resetFilters}
              >
                Resetar
              </button>
              <button
                className="flex-1 bg-purple-600 hover:bg-purple-700 text-white rounded-lg py-2 px-4 font-medium transition-colors duration-200"
                onClick={applyFilters}
              >
                Aplicar
              </button>
            </div>
          </div>
        </div>

        {/* Results Section */}
        <div className="lg:w-2/3">
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-600"></div>
            </div>
          ) : professionals.length > 0 ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {professionals.map((professional) => (
                  <div 
                    key={professional.id}
                    className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border-t-4 border-purple-600"
                  >
                    <div className="p-6">
                      <div className="flex items-center mb-4">
                        {professional.avatar ? (
                          <img 
                            src={professional.avatar} 
                            alt={professional.name} 
                            className="w-12 h-12 rounded-full object-cover mr-4"
                          />
                        ) : (
                          <div className="w-12 h-12 rounded-full bg-purple-600 flex items-center justify-center text-white font-bold mr-4">
                            {professional.name.charAt(0)}
                          </div>
                        )}
                        <div>
                          <h3 className="font-bold text-gray-900">{professional.name}</h3>
                          <div className="flex items-center">
                            <div className="flex">
                              {renderStars(professional.rating)}
                            </div>
                            <span className="text-gray-600 text-sm ml-2">
                              {professional.rating} ({professional.reviewCount})
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      <h4 className="font-bold text-gray-900 mb-2">{professional.service}</h4>
                      <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                        {professional.description}
                      </p>
                      
                      <div className="flex justify-between items-center mb-4">
                        <span className="font-bold text-purple-600">R$ {professional.price.toFixed(2)}</span>
                        <span className="bg-purple-100 text-purple-800 text-xs font-semibold px-2.5 py-0.5 rounded-full">
                          {professional.category}
                        </span>
                      </div>
                      
                      <button className="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center">
                        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                        Solicitar
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Pagination */}
              <div className="mt-8 flex justify-center">
                <nav className="flex items-center space-x-2">
                  <button className="px-3 py-1 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                  </button>
                  {[1, 2, 3].map((page) => (
                    <button 
                      key={page}
                      className={`w-10 h-10 rounded-lg ${
                        page === 1 
                          ? 'bg-purple-600 text-white' 
                          : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                      }`}
                    >
                      {page}
                    </button>
                  ))}
                  <button className="px-3 py-1 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </button>
                </nav>
              </div>
            </>
          ) : (
            <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
              <svg className="w-16 h-16 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 className="text-xl font-bold text-gray-900 mt-4">Nenhum profissional encontrado</h3>
              <p className="text-gray-600 mt-2">Tente ajustar seus filtros ou buscar por outra categoria.</p>
              <button 
                className="mt-6 bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-6 rounded-lg transition-colors duration-200"
                onClick={resetFilters}
              >
                Limpar filtros
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfessionalSearch;