// import React, { useEffect, useRef, useLayoutEffect } from 'react';
// import * as d3 from 'd3';
// import '../assets/GraphVisualizer.css';

// const GraphVisualizer = ({ data, onNodeClick, selectedNodeId }) => {
//   const svgRef = useRef();
//   const containerRef = useRef();

//   useLayoutEffect(() => {
//     if (!data || !data.nodes || !data.links || !containerRef.current) return;

//     const svg = d3.select(svgRef.current);
//     svg.selectAll("*").remove();

//     const { width, height } = containerRef.current.getBoundingClientRect();

//     const simulation = d3.forceSimulation(data.nodes)
//       .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
//       .force("charge", d3.forceManyBody().strength(-250))
//       .force("center", d3.forceCenter(width / 2, height / 2));

//     const link = svg.append("g").attr("class", "links")
//       .selectAll("line").data(data.links).enter().append("line");

//     const node = svg.append("g").attr("class", "nodes")
//       .selectAll("circle").data(data.nodes).enter().append("circle")
//       .attr("r", 12)
//       .attr("class", d => d.id === selectedNodeId ? 'node selected' : 'node')
//       .on("click", (event, d) => {
//         onNodeClick(d);
//       })
//       .call(d3.drag()
//         .on("start", dragstarted)
//         .on("drag", dragged)
//         .on("end", dragended));

//     node.append("title").text(d => d.id);

//     simulation.on("tick", () => {
//       link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
//           .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
//       node.attr("cx", d => d.x).attr("cy", d => d.y);
//     });

//     function dragstarted(event, d) {
//       if (!event.active) simulation.alphaTarget(0.3).restart();
//       d.fx = d.x; d.fy = d.y;
//     }
//     function dragged(event, d) {
//       d.fx = event.x; d.fy = event.y;
//     }
//     function dragended(event, d) {
//       if (!event.active) simulation.alphaTarget(0);
//       d.fx = null; d.fy = null;
//     }

//   }, [data, selectedNodeId, onNodeClick]);

//   return (
//     <div ref={containerRef} className="graph-container">
//       <svg ref={svgRef} style={{ width: '100%', height: '100%' }}></svg>
//     </div>
//   );
// };

// export default GraphVisualizer;

import React, { useEffect, useRef, useLayoutEffect } from 'react';
import * as d3 from 'd3';
import '../assets/GraphVisualizer.css';

const GraphVisualizer = ({ data, onNodeClick, selectedNodeId, highlightedNodes = [] }) => {
  const svgRef = useRef();
  const containerRef = useRef();

  useLayoutEffect(() => {
    if (!data || !data.nodes || !data.links || !containerRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const { width, height } = containerRef.current.getBoundingClientRect();

    const simulation = d3.forceSimulation(data.nodes)
      .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-250))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg.append("g").attr("class", "links")
      .selectAll("line").data(data.links).enter().append("line");

    // Helper function to determine the CSS class for a node
    const getNodeClass = (d) => {
      let classes = 'node';
      if (d.id === selectedNodeId) {
        classes += ' selected';
      } else if (highlightedNodes.includes(d.id)) {
        classes += ' highlighted';
      }
      return classes;
    };

    const node = svg.append("g").attr("class", "nodes")
      .selectAll("circle").data(data.nodes).enter().append("circle")
      .attr("r", 12)
      .attr("class", getNodeClass) // Use the helper function here
      .on("click", (event, d) => {
        onNodeClick(d);
      })
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    node.append("title").text(d => d.id);

    simulation.on("tick", () => {
      link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
          .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
      node.attr("cx", d => d.x).attr("cy", d => d.y);
    });

    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x; d.fy = d.y;
    }
    function dragged(event, d) {
      d.fx = event.x; d.fy = event.y;
    }
    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null; d.fy = null;
    }

  }, [data, selectedNodeId, onNodeClick, highlightedNodes]);

  return (
    <div ref={containerRef} className="graph-container">
      <svg ref={svgRef} style={{ width: '100%', height: '100%' }}></svg>
    </div>
  );
};

export default GraphVisualizer;
