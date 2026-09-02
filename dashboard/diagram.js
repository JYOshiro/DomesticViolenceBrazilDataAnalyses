(() => {
  if (!window.mermaid) return;

  window.mermaid.initialize({
    startOnLoad: false,
    securityLevel: 'strict',
    theme: 'base',
    flowchart: {
      curve: 'stepBefore',
      htmlLabels: true,
      nodeSpacing: 40,
      rankSpacing: 64,
      padding: 20,
      useMaxWidth: false
    },
    themeVariables: {
      background: '#142129',
      primaryColor: '#1a2a33',
      primaryTextColor: '#f1f4f2',
      primaryBorderColor: '#30434d',
      lineColor: '#b6c1be',
      textColor: '#f1f4f2',
      edgeLabelBackground: '#142129',
      fontFamily: 'Manrope, sans-serif',
      fontSize: '22px'
    },
    themeCSS: `
      .nodeLabel, .nodeLabel p { font-size: 22px !important; font-weight: 600; line-height: 1.35; }
      .edgeLabel, .edgeLabel p { color: #f1f4f2; font-size: 20px !important; font-weight: 700; }
      .flowchart-link { stroke-linecap: round; stroke-linejoin: round; }
    `
  });

  window.mermaid.run({ querySelector: '.mermaid' }).catch(error => {
    console.error('Investigation process diagram could not be rendered.', error);
  });
})();
