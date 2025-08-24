import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import '../assets/GraphVisualizer.css';

const GraphVisualizer = ({ data }) => {
  const svgRef = useRef();

  useEffect(() => {
    if (!data || !data.nodes || !data.links) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove(); // Clear previous graph

    const width = parseInt(svg.style("width"));
    const height = parseInt(svg.style("height"));

    const simulation = d3.forceSimulation(data.nodes)
      .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-200))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg.append("g")
      .attr("class", "links")
      .selectAll("line")
      .data(data.links)
      .enter().append("line")
      .attr("stroke-width", 2);

    const node = svg.append("g")
      .attr("class", "nodes")
      .selectAll("circle")
      .data(data.nodes)
      .enter().append("circle")
      .attr("r", 10)
      .call(d3.drag()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended));

    node.append("title")
      .text(d => d.id);

    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);
    });

    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

  }, [data]);

  return (
    <div className="graph-container">
      <svg ref={svgRef} style={{ width: '100%', height: '500px' }}></svg>
    </div>
  );
};

export default GraphVisualizer;
