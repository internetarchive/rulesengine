
/*
   SURT Navigation
 */

function getSurtNavChangeHandler(surtNavEl) {
  // Collect the ordered <select> elements.
  const selectEls = Array.from(surtNavEl.children)

  surtNavEl.addEventListener("change", e => {
    const el = e.target
    let partIdx = parseInt(el.name.split('-')[1])
    if (el.value === "") {
      partIdx -= 1
    }
    // Clear search string altogether if truncate was selected in
    // the first (i.e. protocol) field.
    if (partIdx === -1) {
      window.location.search = ''
      return
    }
    // Generate a new surt up to the selected part index.
    let surt = (
      selectEls[0].value
      + "://("
      + selectEls.slice(1, partIdx + 1)
                  .map(el => el.value)
                  .join(',')
    )
    window.location.search = "?q=" + surt
  })
}

function initSurtNav () {
  const surtNavEl = document.getElementById("surt-part-navigator")
  surtNavEl.addEventListener("change", getSurtNavChangeHandler(surtNavEl))
}

/*
   Field Filters
 */

function getFilterCellFieldValue (el) {
  /* Return a [ <fieldName>, <fieldValue> ] array for the specified cell
     element.
   */
  const name = Array.from(el.classList)
                    .filter(x => x.startsWith('field-'))[0].slice(6)
  const value = el.textContent
  return [ name, value ]
}

function addFilterCellClass (filterFields, appliedFilters) {
  // Add the "filterable-cell" class to all non-empty filterable cells and
  // the "active" to any cells with a corresponding active filter.
  filterFields.forEach(field => {
    Array.from(document.querySelectorAll(`td.field-${field}`))
         .filter(el => el.textContent.trim() !== "")
         .forEach(el => {
           el.classList.add("filterable-cell")
           const [ name, value ] = getFilterCellFieldValue(el)
           if (appliedFilters.has(name)
               && appliedFilters.get(name) === value) {
             el.classList.add("active")
           }
         })
  })
}

function registerFilterCellClickHandler () {
  const tableEl = document.getElementById("result_list")
  if (tableEl === null) {
    // Table is not present when there are no search results.
    return
  }
  tableEl.addEventListener("click", e => {
    const el = e.target
    if (el.tagName !== "TD" || !el.classList.contains('filterable-cell')) {
      return
    }
    // Update the location.search with the updated params.
    const params = new URLSearchParams(window.location.search)
    const [ name, value ] = getFilterCellFieldValue(el)
    if (el.classList.contains("active")) {
      // Remove the param if already active.
      params.delete(name)
    }
    else {
      // Add the param.
      params.set(name, value)
    }
    window.location.search = params.toString()
  })
}

function initFilters () {
  const FILTER_FIELDS = ["collection", "partner"]

  // Get any currently applied filters.
  const params = new URLSearchParams(window.location.search)
  const appliedFilters = new Map()
  FILTER_FIELDS.forEach(field => {
    if (params.has(field)) {
      appliedFilters.set(field, params.get(field))
    }
  })

  addFilterCellClass(FILTER_FIELDS, appliedFilters)
  registerFilterCellClickHandler()
}

/*
   Init
 */

document.addEventListener("DOMContentLoaded", () => {
  initSurtNav()
  initFilters()
})
