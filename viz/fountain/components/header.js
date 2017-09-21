import React, {PureComponent} from 'react';
import classnames from 'classnames';

export default class Header extends PureComponent {

  constructor(props) {
    super(props);
    this.state = {}
  }

  renderTabs() {
    const {tabs, selectedTab, onTabClick} = this.props;

    return tabs.map((tab, index) => {
      const tabClass = classnames('tab-item', { 
        selected: selectedTab === index 
      });

      return (
        <div 
          className={tabClass} 
          key={'tab-item-' + index}
          onClick={() => onTabClick(index)}
        >
          <div className="tab-title">{tab.title}</div>
        </div>
      )
    });
  }

  render() {
    const {siteTitle} = this.props;

    return (
      <div className="header">
        <div className="site-title">{siteTitle}</div>
        <div className="site-tabs">
          {this.renderTabs()}
        </div>
      </div>
    );
  }
}

Header.defaultProps = {
  selectedTab: 1,
  onTabClick: () => {},
  tabs: []
};
