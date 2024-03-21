import React, { useState, useEffect } from "react";
import { useLocation, useParams } from "react-router-dom";
import {
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
} from "@nextui-org/react";

const Content = ({ marginTop = "20px" }) => {
  const location = useLocation();
  const [stockInfo, setStockInfo] = useState([]);
  const { ticker } = useParams();

  const isSummaryPage =
    location.pathname.includes("summary") || typeof ticker === "undefined";

  console.log({
    location,
    stockInfo,
    isSummaryPage,
    ticker,
  });

  useEffect(() => {
    // Check if the ticker is defined before attempting to fetch stock info
    if (ticker) {
      fetch(`https://mcsbt-integration-vr.ew.r.appspot.com/${ticker}`)
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        })
        .then((data) => {
          if (data && data.stock_info) {
            let formattedData = Object.entries(data.stock_info).map(
              ([date, info]) => ({
                date,
                open: info["1. open"],
                high: info["2. high"],
                low: info["3. low"],
                close: info["4. close"],
                volume: info["5. volume"],
              })
            );
            formattedData.sort((a, b) => b.date.localeCompare(a.date));
            setStockInfo(formattedData);
          } else {
            console.error("Missing or invalid stock_info data");
            setStockInfo([]);
          }
        })
        .catch((error) => {
          console.error("Error fetching stock information:", error);
          setStockInfo([]);
        });
    }
  }, [ticker]); // Depend on ticker for re-fetching data

  const displayTicker = ticker ? ticker.toUpperCase() : "N/A";

  if (isSummaryPage) {
    return (
      <div
        style={{
          marginTop,
          width: "100%",
          maxWidth: "800px",
          textAlign: "center",
          color: "green",
          background: "purple",
          padding: "20px",
          borderRadius: "8px",
          boxShadow: "0 4px 14px 0 rgba(0,0,0,0.1)",
        }}
      >
        <h1> LISTOCK</h1>
        <h1> STOCKS CHART LOADING</h1>
      </div>
    );
  }

  return (
    <div style={{ marginTop, width: "100%", maxWidth: "800px" }}>
      <h2
        style={{
          color: "purple",
          margin: "0 0 20px",
          fontWeight: "800",
          fontSize: "20px",
        }}
      >
        {displayTicker} ($)
      </h2>
      <Table aria-label="Stock">
        <TableHeader>
          <TableColumn width="30%">Date</TableColumn>
          <TableColumn width="30%">Open</TableColumn>
          <TableColumn width="30%">High</TableColumn>
          <TableColumn width="30%">Low</TableColumn>
          <TableColumn width="30%">Close</TableColumn>
          <TableColumn width="30%">Volume</TableColumn>
        </TableHeader>
        <TableBody>
          {stockInfo.map((info, index) => (
            <TableRow key={index}>
              <TableCell>{info.date}</TableCell>
              <TableCell>{info.open}</TableCell>
              <TableCell>{info.high}</TableCell>
              <TableCell>{info.low}</TableCell>
              <TableCell>{info.close}</TableCell>
              <TableCell>{info.volume}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

export default Content;
