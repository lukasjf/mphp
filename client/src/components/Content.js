import React, { Component } from "react";
import DataSelection from "./cards/DataSelectionContainer";
import FeatureAnalysis from "./cards/FeatureAnalysisContainer";
import Results from "./cards/ResultsContainer";

class Content extends Component {
  render() {
    return (
      <div className="content">
        <DataSelection />
        <FeatureAnalysis />
        <Results />
      </div>
    );
  }
}

export default Content;
