import {forwardRef} from 'react';

import {SvgIcon, SVGIconProps} from './svgIcon';

const IconExpand = forwardRef<SVGSVGElement, SVGIconProps>((props, ref) => {
  return (
    <SvgIcon {...props} ref={ref}>
      <path d="M14.51,2.56l-3,3a.75.75,0,0,1-1.06,0,.75.75,0,0,1,0-1.06l3-3H11a.76.76,0,0,1-.75-.75A.76.76,0,0,1,11,0h4.24A.76.76,0,0,1,16,.75V5a.75.75,0,0,1-1.5,0Z" />
      <path d="M2.59,1.5,5.52,4.44a.74.74,0,0,1,0,1.06A.75.75,0,0,1,5,5.72a.79.79,0,0,1-.53-.22L1.53,2.56V5A.75.75,0,0,1,0,5V.75A.75.75,0,0,1,.78,0H5A.75.75,0,0,1,5,1.5Z" />
      <path d="M13.42,14.49l-2.93-2.93a.75.75,0,0,1,0-1.06.74.74,0,0,1,1.06,0l2.93,2.93V11A.75.75,0,1,1,16,11v4.21a.74.74,0,0,1-.75.75H11a.75.75,0,0,1,0-1.5Z" />
      <path d="M1.51,13.43l2.91-2.92a.77.77,0,0,1,1.07,0,.75.75,0,0,1,0,1.06L2.57,14.49H5A.75.75,0,1,1,5,16H.76A.74.74,0,0,1,0,15.24V11a.74.74,0,0,1,.75-.75.75.75,0,0,1,.75.75Z" />
    </SvgIcon>
  );
});

IconExpand.displayName = 'IconExpand';

export {IconExpand};
