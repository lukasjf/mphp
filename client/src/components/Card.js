import React, { Component } from "react";
import { Card as _Card, CardTitle, CardText } from "material-ui/Card";
import Spinner from "./Spinner";
import styled from "styled-components";

const CARD_TITLE_HEIGHT = 15;

class Card extends Component {
  render() {
    const { title, isLoading, width } = this.props;
    return (
      <StyledCard zDepth={1} width={width}>
        <StyledCardTitle>
          <StyledTitleText>{title}</StyledTitleText>
          {isLoading ? <Spinner size={CARD_TITLE_HEIGHT} /> : null}
        </StyledCardTitle>
        {isLoading ? null : this.renderContent()}
      </StyledCard>
    );
  }

  renderContent() {
    const { DataViewer, viewerProps } = this.props;
    const isError = viewerProps.data && viewerProps.data.isError;
    return isError ? (
      <StyledError>{`${viewerProps.data.error}`}</StyledError>
    ) : (
      <CardText>
        <DataViewer {...viewerProps} />
      </CardText>
    );
  }
}

const StyledCard = styled(_Card)`
  width: ${props => (props.fitContent ? "fit-content" : null)};
  margin: ${props => props.theme.mediumSpace};
  padding: ${props => props.theme.mediumSpace};
  padding-top: ${props => props.theme.smallSpace};
  padding-bottom: ${props => props.theme.smallSpace};
`;

const StyledCardTitle = styled(CardTitle)`
  display: flex;
  align-items: center;
  height: ${CARD_TITLE_HEIGHT};
`;

const StyledTitleText = styled.p`
  margin-right: ${props => props.theme.mediumSpace};
  font-size: ${props => props.theme.h2};
`;

const StyledError = styled(CardText)`
  color: red !important;
`;

export default Card;
