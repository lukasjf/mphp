import React, { Component } from "react";
import styled from "styled-components";
import _IconButton from "material-ui/IconButton";
import EditIcon from "material-ui/svg-icons/editor/mode-edit";
import OpenIcon from "material-ui/svg-icons/file/folder-open";
import SaveIcon from "material-ui/svg-icons/content/save";
import DeleteIcon from "material-ui/svg-icons/action/delete";
import ClearIcon from "material-ui/svg-icons/content/clear";
import AddIcon from "material-ui/svg-icons/content/add-circle";
import QuestionIcon from "material-ui/svg-icons/action/help-outline";

class IconButton extends Component {
  render() {
    const icons = {
      edit: EditIcon,
      open: OpenIcon,
      save: SaveIcon,
      delete: DeleteIcon,
      add: AddIcon,
      clear: ClearIcon,
      help: QuestionIcon
    };
    const Icon = icons[this.props.icon];

    return (
      <StyledIconButton {...this.props}>
        <Icon />
      </StyledIconButton>
    );
  }
}

const StyledIconButton = styled(_IconButton)`
  width: ${props => props.size || "38px"} !important;
  height: ${props => props.size || "38px"} !important;
  padding: ${props => props.padding || props.theme.smallSpace} !important;
  svg {
    width: 19px !important;
    height: 19px !important;
    color: ${props => props.color || props.textColor} !important;
  }
  cursor: ${props => props.cursor || "pointer"} !important;
`;

export default IconButton;
