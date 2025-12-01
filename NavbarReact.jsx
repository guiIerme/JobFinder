import React, { useState, useEffect, useRef } from 'react';

const Navbar = () => {
  // State for dropdown visibility
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  
  // Ref for dropdown element
  const dropdownRef = useRef(null);
  
  // Toggle dropdown visibility
  const toggleDropdown = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };
  
  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    };
    
    // Add event listener
    document.addEventListener('mousedown', handleClickOutside);
    
    // Cleanup event listener
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);
  
  return (
    <nav className="bg-white shadow-lg py-4 transition-all duration-300">
      <div className="container mx-auto px-4">
        <div className="flex flex-wrap items-center justify-between">
          {/* Logo */}
          <a href="#" className="flex items-center space-x-2 text-purple-600 font-bold text-xl">
            <i className="fas fa-toolbox text-2xl"></i>
            <span>Job Finder</span>
          </a>
          
          {/* Hamburger button for mobile */}
          <button 
            className="lg:hidden text-gray-700 focus:outline-none"
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
          >
            <i className="fas fa-bars text-2xl"></i>
          </button>
          
          {/* Navigation links - hidden on mobile, visible on large screens */}
          <div className={`w-full lg:w-auto lg:flex lg:items-center lg:justify-between ${isDropdownOpen ? 'block' : 'hidden'}`}>
            <ul className="flex flex-col lg:flex-row lg:space-x-2 py-4 lg:py-0">
              <li>
                <a href="#" className="block py-2 px-4 text-gray-800 font-medium rounded-lg hover:bg-purple-100 hover:text-purple-600 transition-all duration-300">Início</a>
              </li>
              <li>
                <a href="#" className="block py-2 px-4 text-gray-800 font-medium rounded-lg hover:bg-purple-100 hover:text-purple-600 transition-all duration-300">Buscar Profissionais</a>
              </li>
              <li>
                <a href="#" className="block py-2 px-4 text-gray-800 font-medium rounded-lg hover:bg-purple-100 hover:text-purple-600 transition-all duration-300">Parceiros</a>
              </li>
              <li>
                <a href="#" className="block py-2 px-4 text-gray-800 font-medium rounded-lg hover:bg-purple-100 hover:text-purple-600 transition-all duration-300">Sobre</a>
              </li>
              <li>
                <a href="#" className="block py-2 px-4 text-gray-800 font-medium rounded-lg hover:bg-purple-100 hover:text-purple-600 transition-all duration-300">Contato</a>
              </li>
              <li>
                <a href="#" className="block py-2 px-4 text-gray-800 font-medium rounded-lg hover:bg-purple-100 hover:text-purple-600 transition-all duration-300">Blog</a>
              </li>
            </ul>
            
            {/* User profile section */}
            <div className="relative flex items-center mt-4 lg:mt-0" ref={dropdownRef}>
              <div 
                className="flex items-center space-x-3 cursor-pointer py-2 px-4 rounded-lg hover:bg-gray-100 transition-all duration-300"
                onClick={toggleDropdown}
              >
                <div className="w-10 h-10 rounded-full bg-purple-600 text-white flex items-center justify-center font-bold text-lg">
                  i
                </div>
                <span className="text-gray-800 font-medium">isaque</span>
              </div>
              
              {/* Dropdown menu with smooth transition */}
              {isDropdownOpen && (
                <div className="absolute right-0 top-full mt-2 w-48 bg-white rounded-lg shadow-xl border border-gray-200 py-2 transition-all duration-300 ease-in-out transform origin-top">
                  <a href="#" className="flex items-center px-4 py-3 text-gray-800 hover:bg-purple-100 transition-colors duration-200">
                    <i className="fas fa-user mr-3 text-gray-600"></i>
                    <span>Meu Perfil</span>
                  </a>
                  <a href="#" className="flex items-center px-4 py-3 text-gray-800 hover:bg-purple-100 transition-colors duration-200">
                    <i className="fas fa-cog mr-3 text-gray-600"></i>
                    <span>Configurações</span>
                  </a>
                  <hr className="my-2 border-gray-200" />
                  <a href="#" className="flex items-center px-4 py-3 text-gray-800 hover:bg-purple-100 transition-colors duration-200">
                    <i className="fas fa-sign-out-alt mr-3 text-gray-600"></i>
                    <span>Sair</span>
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;