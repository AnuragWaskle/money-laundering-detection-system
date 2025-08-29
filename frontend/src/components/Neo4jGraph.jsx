import React from 'react';
import { FaShareAlt, FaProjectDiagram, FaMousePointer } from 'react-icons/fa';
import '../assets/Neo4jGraph.css';

const Neo4jGraph = ({ caseId }) => {
  // In a real-world production application, this component would use a library
  // like 'neovis.js' or another graph visualization library to render data
  // fetched directly from the Neo4j database.

  // For our project, we are displaying a placeholder that represents this
  // live, interactive visualization.

  return (
    <div className="neo4j-graph-container">
      <div className="graph-toolbar">
        <button className="toolbar-btn"><FaMousePointer /> Select</button>
        <button className="toolbar-btn"><FaShareAlt /> Expand</button>
        <span className="case-id-display">Displaying Graph for: <strong>{caseId || 'CASE-001'}</strong></span>
      </div>
      <div className="graph-viewport">
        <FaProjectDiagram size={100} />
        <p>Live Interactive Neo4j Graph</p>
        <span>(Placeholder for embedded visualization)</span>
      </div>
    </div>
  );
};

export default Neo4jGraph;
