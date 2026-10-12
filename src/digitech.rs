use base::config::keys;
use hbb_common::config;

pub const APP_NAME: &str = "DigiDesk";
pub const DISPLAY_NAME: &str = "Digitech - Assistenza Remota";
const SERVER: &str = "cloud-hub.digitech-group.com";
const KEY: &str = "vUrYF3I2VLgVB6qFlQUzjJIX152Ey1yUAX24+dwGDzs=";

// Same tables a signed custom.txt fills on a Pro custom client, set at build time instead.
pub fn apply() {
    *config::APP_NAME.write().unwrap() = APP_NAME.to_owned();
    *config::PROD_RENDEZVOUS_SERVER.write().unwrap() = SERVER.to_owned();

    let mut overwrite = config::OVERWRITE_SETTINGS.write().unwrap();
    for (k, v) in [
        (keys::OPTION_CUSTOM_RENDEZVOUS_SERVER, SERVER),
        (keys::OPTION_RELAY_SERVER, SERVER),
        (keys::OPTION_API_SERVER, ""),
        (keys::OPTION_KEY, KEY),
        (keys::OPTION_APPROVE_MODE, "password"),
        (keys::OPTION_VERIFICATION_METHOD, "use-temporary-password"),
        (keys::OPTION_ALLOW_REMOTE_CONFIG_MODIFICATION, "N"),
        (keys::OPTION_ENABLE_LAN_DISCOVERY, "N"),
        (keys::OPTION_DIRECT_SERVER, "N"),
    ] {
        overwrite.insert(k.to_owned(), v.to_owned());
    }
    drop(overwrite);

    config::OVERWRITE_LOCAL_SETTINGS
        .write()
        .unwrap()
        .insert(keys::OPTION_ENABLE_CHECK_UPDATE.to_owned(), "N".to_owned());

    let mut hard = config::HARD_SETTINGS.write().unwrap();
    for (k, v) in [
        ("conn-type", "incoming"),
        ("disable-settings", "Y"),
        ("disable-installation", "Y"),
        ("disable-account", "Y"),
        ("disable-ab", "Y"),
    ] {
        hard.insert(k.to_owned(), v.to_owned());
    }
    drop(hard);

    let mut builtin = config::BUILTIN_SETTINGS.write().unwrap();
    for k in [
        keys::OPTION_HIDE_SERVER_SETTINGS,
        keys::OPTION_HIDE_NETWORK_SETTINGS,
        keys::OPTION_HIDE_PROXY_SETTINGS,
        keys::OPTION_HIDE_WEBSOCKET_SETTINGS,
        keys::OPTION_HIDE_SECURITY_SETTINGS,
        keys::OPTION_HIDE_HELP_CARDS,
        keys::OPTION_HIDE_POWERED_BY_ME,
        keys::OPTION_DISABLE_CHANGE_PERMANENT_PASSWORD,
        keys::OPTION_DISABLE_CHANGE_ID,
    ] {
        builtin.insert(k.to_owned(), "Y".to_owned());
    }
    builtin.insert(
        keys::OPTION_ALLOW_DEEP_LINK_SERVER_SETTINGS.to_owned(),
        "N".to_owned(),
    );
}

pub fn translate(lang: &str, name: &str) -> Option<String> {
    let it = lang == "it";
    let s = match name {
        "Your Desktop" => DISPLAY_NAME,
        "desk_tip" if it => {
            "Comunica questo ID e la password all'operatore Digitech per ricevere assistenza."
        }
        "desk_tip" => "Give this ID and password to the Digitech operator to receive support.",
        _ => return None,
    };
    Some(s.to_owned())
}
