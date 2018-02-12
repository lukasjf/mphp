import React, { Component } from "react";
import SelectField from "material-ui/SelectField";
import MenuItem from "material-ui/MenuItem";
import TextField from "material-ui/TextField";
import Checkbox from "material-ui/Checkbox";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import HelpIcon from "material-ui/svg-icons/action/help-outline";

import Description from "../../Description";
import TooltipBox from "../../TooltipBox";
import { boringBlue } from "../../../config/colors";
import { canRunOneAgainstAll } from "../../../utils";

export default class AlgorithmSelection extends Component {
  render() {
    const { algorithms, algorithm, datasets, dataset } = this.props;

    // preselect one algorithm for faster debugging
    // TODO: remove in the end
    if (!algorithm.key) {
      algorithm.key = "norm"
      algorithm.name = "Normalized Feature Selection"
      algorithm.parameters = {
        "k": 10,
        "n": 5000,
        "norm": "exclude"
      }
    }

    return (
      <StyledMenu>
        <StyledOptions>
          <StyledSelectField
            floatingLabelText="Dataset"
            floatingLabelFixed={true}
            hintText="Select dataset..."
            value={dataset || null}
            onChange={this.changeDataset.bind(this)}
            autoWidth={true}
            selectedMenuItemStyle={{ color: boringBlue }}
            disabled={this.props.disabled}
            style={{ width: 220 }}
          >
            {Object.keys(datasets).map(dataset => (
              <MenuItem
                key={dataset}
                value={dataset}
                primaryText={datasets[dataset]}
              />
            ))}
          </StyledSelectField>
          <StyledSelectField
            floatingLabelText="Algorithm"
            floatingLabelFixed={true}
            hintText="Select algorithm..."
            value={algorithm.key || null}
            onChange={this.selectAlgorithm.bind(this)}
            autoWidth={true}
            selectedMenuItemStyle={{ color: boringBlue }}
            disabled={this.props.disabled}
            style={{ width: 220 }}
          >
            {Object.keys(algorithms).map(this.renderMenuItem.bind(this))}
          </StyledSelectField>
          {algorithm.key &&
            algorithms &&
            Object.keys(algorithms[algorithm.key].parameters).map(
              this.renderParameter.bind(this)
            )}
          {algorithm.key &&
            algorithms && (
              <StyledAlgorithmDescription>
                <FormattedMessage id={`Algorithms.${algorithm.key}`} />
              </StyledAlgorithmDescription>
            )}
        </StyledOptions>
        {this.renderComparisonModeSelection()}
      </StyledMenu>
    );
  }

  renderMenuItem(algorithm, index) {
    // TODO only render if sufficient cancer and tissue types are selected (see #61)
    return (
      <MenuItem
        key={`algorithm-option-${index}`}
        value={algorithm}
        primaryText={this.props.algorithms[algorithm].name}
      />
    );
  }

  renderParameter(parameterName, index) {
    const { algorithms, algorithm } = this.props;
    const parameter = algorithms[algorithm.key].parameters[parameterName];
    if (parameter.available) {
      return this.renderTextSelectionParameter(parameterName, index);
    } else {
      return this.renderNumericParameter(parameterName, index);
    }
  }

  renderTextSelectionParameter(parameterName, index) {
    const { disabled, algorithms, algorithm } = this.props;
    const parameter = algorithms[algorithm.key].parameters[parameterName];
    return (
      <StyledParameter key={parameterName}>
        <StyledInnerSelectField
          key={parameterName}
          id={parameterName}
          value={
            this.props.algorithm.parameters[parameterName] || parameter.default
          }
          onChange={this.changeTextSelectionParameter.bind(this, parameterName)}
          floatingLabelText={parameter.name}
          floatingLabelFixed={true}
          autoWidth={true}
          selectedMenuItemStyle={{ color: boringBlue }}
          disabled={disabled}
          style={{ width: 210 }}
        >
          {parameter.available.map(x => {
            return (
              <MenuItem key={x} id={parameterName} value={x} primaryText={x} />
            );
          })}
        </StyledInnerSelectField>
        <TooltipBox
          text={<FormattedMessage id={`Parameters.${parameterName}`} />}
        >
          <HelpIcon />
        </TooltipBox>
      </StyledParameter>
    );
  }

  renderNumericParameter(parameterName, index) {
    const { disabled, algorithms, algorithm } = this.props;
    const parameter = algorithms[algorithm.key].parameters[parameterName];
    return (
      <StyledParameter key={parameterName}>
        <StyledTextField
          id={parameterName}
          value={
            this.props.algorithm.parameters[parameterName] || parameter.default
          }
          hintText={parameter.default}
          floatingLabelText={parameter.name}
          floatingLabelFixed={true}
          type="number"
          onChange={this.changeNumericParameter.bind(this)}
          disabled={disabled}
          style={{ width: 210 }}
        />
        <TooltipBox
          text={<FormattedMessage id={`Parameters.${parameterName}`} />}
        >
          <HelpIcon />
        </TooltipBox>
      </StyledParameter>
    );
  }

  renderComparisonModeSelection() {
    const descriptionText =
      "Enable to select discriminating genes per cancer type against all others (returning one set per cancer type), " +
      "disable to select one set of discriminating genes for all cancer types.";
    return (
      <Description text={descriptionText}>
        <StyledCheckbox
          label="One against rest"
          checked={this.props.oneAgainstRest}
          onCheck={this.toggleComparisonMode.bind(this)}
          iconStyle={{ fill: boringBlue }}
          disabled={!canRunOneAgainstAll(this.props.algorithm)}
        />
      </Description>
    );
  }

  changeDataset(event, index, dataset) {
    const { runId, updateRun } = this.props;
    // necessary because not all cancer types are available in every data set
    const algorithm = {
      cancerTypes: ["THCA"],
      healthyTissueTypes: ["NT"],
      sickTissueTypes: ["TP"]
    };
    updateRun(runId, { dataset: dataset, algorithm: algorithm });
  }

  changeTextSelectionParameter(parameterName, event, index, key) {
    const { algorithm, runId, updateRun } = this.props;
    const updatedParams = {
      ...algorithm.parameters,
      [parameterName]: key
    };
    updateRun(runId, {
      algorithm: { ...algorithm, parameters: updatedParams }
    });
  }

  changeNumericParameter(event, index, key) {
    const { algorithm, runId, updateRun } = this.props;
    const updatedParams = {
      ...algorithm.parameters,
      [event.target.id]: parseInt(event.target.value, 10)
    };
    updateRun(runId, {
      algorithm: { ...algorithm, parameters: updatedParams }
    });
  }

  toggleComparisonMode() {
    const { oneAgainstRest, runId, updateRun } = this.props;
    updateRun(runId, { oneAgainstRest: !oneAgainstRest });
  }

  selectAlgorithm(event, index, key) {
    const { algorithm, algorithms, runId, updateRun } = this.props;
    const parameters = algorithms[key].parameters;
    const updatedValues = {
      name: algorithms[key].name,
      key,
      parameters: Object.keys(parameters).reduce((reducedParams, param) => {
        return { ...reducedParams, [param]: parameters[param].default };
      }, {})
    };
    updateRun(runId, { algorithm: { ...algorithm, ...updatedValues } });
  }
}

const StyledParameter = styled.div`
  display: flex;
  align-items: center;
`;

const StyledAlgorithmDescription = styled.div`
  padding-top: 8px;
  max-width: 220px;
  color: ${props => props.theme.deepGray};
`;

const StyledMenu = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: space-between;
`;

const StyledOptions = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  margin: ${props => props.theme.mediumSpace};
`;

const StyledSelectField = styled(SelectField) `
  button {
    fill: ${props => props.theme.textColor} !important;
  }
`;

const StyledInnerSelectField = styled(SelectField) `
  margin-left: ${props => props.theme.mediumSpace};
`;

const StyledTextField = styled(TextField) `
  margin-left: ${props => props.theme.mediumSpace};
`;

const StyledCheckbox = styled(Checkbox) `
  margin-left: ${props => props.theme.mediumSpace};
`;
