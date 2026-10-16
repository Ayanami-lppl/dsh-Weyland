//#region host half
/**
 * Node half of `dsh-weyland-intro`.
 *
 * A `dsh.client` package still needs a loadable node-side row: the Loader
 * mounts this module for the entry, while the browser half ships through the
 * `./client` export. Everything this plugin does is browser presentation, so
 * the host side stays empty.
 */
function apply() {}
//#endregion
export { apply };
