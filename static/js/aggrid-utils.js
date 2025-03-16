var localeText = {
    // Acessibilidade
    ariaAdvancedFilterBuilderItem: (variableValues) => `${variableValues[0]}. Nível ${variableValues[1]}. Pressione ENTER para editar`,
    ariaAdvancedFilterBuilderItemValidation: (variableValues) => `${variableValues[0]}. Nível ${variableValues[1]}. ${variableValues[2]} Pressione ENTER para editar`,
    ariaAdvancedFilterBuilderList: "Lista de Filtros Avançados",
    ariaAdvancedFilterBuilderFilterItem: "Condição de Filtro",
    ariaAdvancedFilterBuilderGroupItem: "Grupo de Filtro",
    ariaAdvancedFilterBuilderColumn: "Coluna",
    ariaAdvancedFilterBuilderOption: "Opção",
    ariaAdvancedFilterBuilderValue: "Valor",
    ariaAdvancedFilterBuilderJoinOperator: "Operador de Junção",
    ariaAdvancedFilterInput: "Entrada de Filtro Avançado",
    ariaLabelAdvancedFilterAutocomplete: "Autocompletar Filtro Avançado",
    
    // Filtros Avançados
    advancedFilterContains: "contém",
    advancedFilterNotContains: "não contém",
    advancedFilterTextEquals: "igual",
    advancedFilterTextNotEqual: "não igual",
    advancedFilterStartsWith: "começa com",
    advancedFilterEndsWith: "termina com",
    advancedFilterBlank: "está em branco",
    advancedFilterNotBlank: "não está em branco",
    advancedFilterEquals: "=",
    advancedFilterNotEqual: "!=",
    advancedFilterGreaterThan: ">",
    advancedFilterGreaterThanOrEqual: ">=",
    advancedFilterLessThan: "<",
    advancedFilterLessThanOrEqual: "<=",
    advancedFilterTrue: "é verdadeiro",
    advancedFilterFalse: "é falso",
    advancedFilterAnd: "E",
    advancedFilterOr: "OU",
    advancedFilterApply: "Aplicar",
    advancedFilterBuilder: "Construtor",
    
    // Validações de Filtro Avançado
    advancedFilterValidationMissingColumn: "Coluna ausente",
    advancedFilterValidationMissingOption: "Opção ausente",
    advancedFilterValidationMissingValue: "Valor ausente",
    advancedFilterValidationInvalidColumn: "Coluna não encontrada",
    advancedFilterValidationInvalidOption: "Opção não encontrada",
    advancedFilterValidationMissingQuote: "Valor está sem aspas finais",
    advancedFilterValidationNotANumber: "Valor não é um número",
    advancedFilterValidationInvalidDate: "Valor não é uma data válida",
    advancedFilterValidationMissingCondition: "Condição ausente",
    advancedFilterValidationJoinOperatorMismatch: "Operadores de junção dentro de uma condição devem ser iguais",
    advancedFilterValidationInvalidJoinOperator: "Operador de junção não encontrado",
    advancedFilterValidationMissingEndBracket: "Falta parêntese de fechamento",
    advancedFilterValidationExtraEndBracket: "Muitos parênteses de fechamento",
    advancedFilterValidationMessage: (variableValues) => `Expressão contém um erro. ${variableValues[0]} - ${variableValues[1]}.`,
    advancedFilterValidationMessageAtEnd: (variableValues) => `Expressão contém um erro. ${variableValues[0]} no final da expressão.`,
    
    // Construtor de Filtro Avançado
    advancedFilterBuilderTitle: "Filtro Avançado",
    advancedFilterBuilderApply: "Aplicar",
    advancedFilterBuilderCancel: "Cancelar",
    advancedFilterBuilderAddButtonTooltip: "Adicionar Filtro ou Grupo",
    advancedFilterBuilderRemoveButtonTooltip: "Remover",
    advancedFilterBuilderMoveUpButtonTooltip: "Mover para Cima",
    advancedFilterBuilderMoveDownButtonTooltip: "Mover para Baixo",
    advancedFilterBuilderAddJoin: "Adicionar Grupo",
    advancedFilterBuilderAddCondition: "Adicionar Filtro",
    advancedFilterBuilderSelectColumn: "Selecione uma coluna",
    advancedFilterBuilderSelectOption: "Selecione uma opção",
    advancedFilterBuilderEnterValue: "Digite um valor...",
    advancedFilterBuilderValidationAlreadyApplied: "Filtro atual já aplicado.",
    advancedFilterBuilderValidationIncomplete: "Nem todas as condições estão completas.",
    advancedFilterBuilderValidationSelectColumn: "Deve selecionar uma coluna.",
    advancedFilterBuilderValidationSelectOption: "Deve selecionar uma opção.",
    advancedFilterBuilderValidationEnterValue: "Deve digitar um valor.",
  
    // Menus
    pinColumn: 'Fixar Coluna',
    valueAgg: 'Valor Agregado',
    autosizeThisColumn: 'Autoajustar Esta Coluna',
    autosizeAllColumns: 'Autoajustar Todas as Colunas',
    groupBy: 'Agrupar por',
    ungroupBy: 'Desagrupar por',
    sortAscending: 'Ordem Crescente',
    sortDescending: 'Ordem Decrescente',
    resetColumns: 'Redefinir Colunas',
    expandAll: 'Expandir Todos',
    collapseAll: 'Recolher Todos',
    toolPanel: 'Painel de Ferramentas',
    export: 'Exportar',
    csvExport: 'Exportar CSV',
    excelExport: 'Exportar Excel (.xlsx)',
    excelXmlExport: 'Exportar Excel (.xml)',
    copy: 'Copiar',
    copyWithHeaders: 'Copiar com Cabeçalhos',
    copyWithGroupHeaders: 'Copiar com Grupo de Cabeçalhos',
    cut: 'Recortar',
    ctrlC: 'Ctrl+C',
    paste: 'Colar',
    ctrlV: 'Ctrl+V',
    columnChooser: 'Escolher Colunas',
    sortUnSort: 'Limpar Ordenamento',
    noPin: 'Não Fixar',
    pinLeft: 'Fixar a Esquerda',
    pinRight: 'Fixar a Direita',
  
    // Painéis
    columns: 'Colunas',
    filters: 'Filtros',
    pivotMode: 'Modo Pivot',
    groups: 'Grupos de Linhas',
    rowGroupColumnsEmptyMessage: 'Arraste aqui para definir grupos de linhas',
    values: 'Valores',
    valueColumnsEmptyMessage: 'Arraste aqui para agregar',
    pivots: 'Rótulos de Coluna',
    pivotColumnsEmptyMessage: 'Arraste aqui para definir rótulos de coluna',
  
    // Filtros
    selectAll: 'Selecionar Tudo',
    selectAllSearchResults: 'Selecionar Todos os Resultados da Busca',
    searchOoo: 'Procurar...',
    blanks: 'Em branco',
    noMatches: 'Sem Resultados',
    
    // Filtros Numéricos e de Texto
    filterOoo: 'Filtrar...',
    applyFilter: 'Aplicar Filtro...',
  
    // Filtros Numéricos
    equals: 'Igual',
    notEqual: 'Diferente',
    lessThan: 'Menor que',
    greaterThan: 'Maior que',
    lessThanOrEqual: 'Menor ou igual',
    greaterThanOrEqual: 'Maior ou igual',
    inRange: 'No intervalo',
  
    // Filtros de Texto
    contains: 'Contém',
    notContains: 'Não contém',
    startsWith: 'Começa com',
    endsWith: 'Termina com',
  
    // Filtros de Data
    dateFormatOoo: 'aaaa-mm-dd',
  
    // Condições de Filtro
    andCondition: 'E',
    orCondition: 'OU',
  
    // Botões de Filtro
    applyFilter: 'Aplicar',
    resetFilter: 'Redefinir',
    clearFilter: 'Limpar',
    cancelFilter: 'Cancelar',
  
    // Títulos de Filtro
    textFilter: 'Filtro de Texto',
    numberFilter: 'Filtro Numérico',
    dateFilter: 'Filtro de Data',
    setFilter: 'Filtro de Conjunto',
  
    // Barras de Status e Agregação
    noRowsToShow: 'Nenhuma linha para mostrar',
  
    // Gráficos
    pivotChartAndPivotMode: 'Gráfico Pivot & Modo Pivot',
    pivotChart: 'Gráfico Pivot',
    chartRange: 'Intervalo do Gráfico',
    chartSettings: 'Configurações do Gráfico',
    chartType: 'Tipo de Gráfico',
    chartTitle: 'Título do Gráfico',
    chartBackground: 'Fundo do Gráfico',
    chartSeries: 'Séries',
    chartAxes: 'Eixos',
    chartLegend: 'Legenda',
    chartOptions: 'Opções',
    menu: 'Menu',
    chart: 'Gráfico',
    groupedColumn: 'Coluna Agrupada',
    stackedColumn: 'Coluna Empilhada',
    normalizedColumn: 'Coluna Normalizada',
    groupedBar: 'Barra Agrupada',
    stackedBar: 'Barra Empilhada',
    normalizedBar: 'Barra Normalizada',
    pieChart: 'Gráfico de Pizza',
    donutChart: 'Gráfico de Donut',
    line: 'Linha',
    xyChart: 'XY (Dispersão)',
    scatter: 'Dispersão',
    bubble: 'Bolhas',
    area: 'Área',
    stackedArea: 'Área Empilhada',
    normalizedArea: 'Área Normalizada',
    histogram: 'Histograma',
  };
  

  function toTitleCase(str) {
    return str.replace(/_/g, ' ').toLowerCase().replace(/\b(\w)/g, s => s.toUpperCase());
}


function formatNumber(params) {
  if (params.value !== undefined && params.value !== null) {
      return params.value.toLocaleString('pt-BR', {
          minimumFractionDigits: 2,  // Define a quantidade mínima de casas decimais
          maximumFractionDigits: 2   // Define a quantidade máxima de casas decimais
      });
  }
  return params.value;
}