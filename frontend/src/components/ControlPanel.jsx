<<<<<<< HEAD
// import React, { useState } from 'react';
// import FileUpload from './FileUpload';
// import Button from './Button';
// import { FaSearch } from 'react-icons/fa';
// import '../assets/ControlPanel.css';

// const ControlPanel = ({ onFileUpload, onSearch }) => {
//   const [searchTerm, setSearchTerm] = useState('');

//   const handleSearch = (e) => {
//     e.preventDefault();
//     if (searchTerm) {
//       onSearch(searchTerm);
//     }
//   };

//   return (
//     <div className="control-panel">
//       <div className="panel-section">
//         <h3>Investigate Account</h3>
//         <form className="search-form" onSubmit={handleSearch}>
//           <input
//             type="text"
//             placeholder="Enter Account ID (e.g., C12345)"
//             value={searchTerm}
//             onChange={(e) => setSearchTerm(e.target.value)}
//           />
//           <button type="submit"><FaSearch /></button>
//         </form>
//       </div>

//       <div className="panel-section">
//         <h3>Ingest Data</h3>
//         <FileUpload onFileUpload={onFileUpload} />
//       </div>
      
//       <div className="panel-section">
//         <h3>Analysis Tools</h3>
//         <Button variant="secondary">Highlight Cycles</Button>
//         <Button variant="secondary">Show High-Risk Nodes</Button>
//       </div>
//     </div>
//   );
// };

// export default ControlPanel;



=======
>>>>>>> 878aa4807e99ba5a524b32f89c231a7c1196f533
import React, { useState } from 'react';
import FileUpload from './FileUpload';
import Button from './Button';
import { FaSearch } from 'react-icons/fa';
import '../assets/ControlPanel.css';

<<<<<<< HEAD
const ControlPanel = ({ onFileUpload, onSearch, onHighlightCycles, onShowHighRiskNodes }) => {
=======
const ControlPanel = ({ onFileUpload, onSearch }) => {
>>>>>>> 878aa4807e99ba5a524b32f89c231a7c1196f533
  const [searchTerm, setSearchTerm] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchTerm) {
      onSearch(searchTerm);
    }
  };

  return (
    <div className="control-panel">
      <div className="panel-section">
        <h3>Investigate Account</h3>
        <form className="search-form" onSubmit={handleSearch}>
          <input
            type="text"
            placeholder="Enter Account ID (e.g., C12345)"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button type="submit"><FaSearch /></button>
        </form>
      </div>

      <div className="panel-section">
        <h3>Ingest Data</h3>
        <FileUpload onFileUpload={onFileUpload} />
      </div>
      
      <div className="panel-section">
        <h3>Analysis Tools</h3>
<<<<<<< HEAD
        <Button variant="secondary" onClick={onHighlightCycles}>
          Highlight Cycles
        </Button>
        <Button variant="secondary" onClick={onShowHighRiskNodes}>
          Show High-Risk Nodes
        </Button>
=======
        <Button variant="secondary">Highlight Cycles</Button>
        <Button variant="secondary">Show High-Risk Nodes</Button>
>>>>>>> 878aa4807e99ba5a524b32f89c231a7c1196f533
      </div>
    </div>
  );
};

export default ControlPanel;
