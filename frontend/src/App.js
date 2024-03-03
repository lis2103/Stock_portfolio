import React, { useState, useEffect } from "react";
import "./App.css"; // Ensure your CSS file is correctly linked

function App() {
  const [portfolio, setPortfolio] = useState({ totalValue: 0, symbols: [] });
  const [selectedSymbolData, setSelectedSymbolData] = useState(null);

  useEffect(() => {
    // Fetch portfolio data
    fetch(`${process.env.REACT_APP_BACKEND_URL}/portfolio_symbols`)
      .then((response) => response.json())
      .then((data) =>
        setPortfolio({
          totalValue: data.total_portfolio_value,
          symbols: data.stocks,
        })
      )
      .catch((error) => console.error("Error:", error));
  }, []);

  const handleSymbolClick = (ticker) => {
    // Fetch data for selected symbol
    fetch(`${process.env.REACT_APP_BACKEND_URL}/weekly_series/${ticker}`)
      .then((response) => response.json())
      .then((data) => setSelectedSymbolData(data))
      .catch((error) => console.error("Error:", error));
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to LIStock</h1>
        <p>Total Portfolio Value: {portfolio.totalValue}</p>
        <ul className="symbol-list">
          {portfolio.symbols.map((symbol) => (
            <li
              key={symbol.ticker}
              onClick={() => handleSymbolClick(symbol.ticker)}
            >
              {symbol.ticker}
            </li>
          ))}
        </ul>
        {selectedSymbolData && <SymbolDetails data={selectedSymbolData.data} />}
      </header>
    </div>
  );
}

function SymbolDetails({ data }) {
  // Assuming 'data' is an object with dates as keys and is sorted from oldest to newest
  const entries = Object.entries(data);
  const mostRecentEntries = entries.length > 2 ? entries.slice(-2) : entries; // Get last two entries
  return (
    <div className="symbol-details">
      {mostRecentEntries.map(([date, details]) => (
        <div key={date} className="week-data">
          <h3>{date}</h3>
          <p>Open: {details["1. open"]}</p>
          <p>High: {details["2. high"]}</p>
          <p>Low: {details["3. low"]}</p>
          <p>Close: {details["4. close"]}</p>
        </div>
      ))}
    </div>
  );
}

export default App;
