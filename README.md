[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

# TESMart TCPIP Control

This component enables control of Tesmart LAN 232 devices including KVMs, Matrixes, and Switches.

Included, but not limited to, are:

- **4x1 DVI KVM Control Panel** (DKS0401A30)
- **8x1 HDMI KVM Control Panel** (HKS0801A30, HKS0801A20, HKE0802A10, HKS0801A40)
- **8x1 HDMI Switch (KVM) Controller** (HSW0801A10, HSW0801A1U, HKS0801A1U)
- **16x1 HDMI Switch Controller** (HKS1601A10, HSW1601A10, HKS1601A1U, HSW1601A1U)
- **Matrix**:
  - **4x4 HDMI Matrix Control Panel V2** (HMA0404A40, HMA0404B40, HMA0404B50, HMA0404B30, HME040410H, HME040806R, HMA0404A1U, HMA0404A70, HMA0404A60)
  - **8x8 HDMI Matrix Control Panel V2** (HMA0808A10, HMA0808A20, HMA0808A30, HMA0808A1U)
- **16x16 Matrix Controller** (HMA1616A10, HMA1616A20)

## Installation

### Upgrading from version 0.0.1.

If you are upgrading from version 0.0.1:
1. Remove the old integration which is /custom_components/tesmart-kvm-homeassistant/ and then install the latest version of the integration.
1. Update the platform configuration in your configuration.yaml file from `tesmart_kvm` to `tesmart_lan`.

### Installation via HACS
Unless you have a good reason not to, you probably want to install this component via HACS(Home Assistant Community Store)
1. Ensure that [HACS](https://hacs.xyz/) is installed.
1. Navigate to HACS -> Integrations
1. Open the three-dot menu and select 'Custom Repositories'
1. Put 'https://github.com/lululombard/tesmart-lan-homeassistant/' into the 'Repository' textbox.
1. Select 'Integration' as the category
1. Press 'Add'.
1. Find the tesmart-lan-homeassistant integration in the HACS integration list and install it
1. Restart Home Assistant.
1. Add the below configuration examples to your configuration.yaml and secrets.yaml file

### Manual Installation
1. Copy all files in `custom_components/tesmart_lan` to your `<config directory>/custom_components/tesmart_lan/` directory.
1. Restart Home-Assistant.
1. Add the configuration to your configuration.yaml and secrets.yaml.
1. Restart Home-Assistant again.

### Configuration
Add the following to your configuration.yaml file changing the values for friendly_name, host ip, and the source names. Note: this example makes use of the secrets.yaml file.

```yaml
media_player:
  - platform: tesmart_lan
    lans:
      tesmart_hdmi_switch:
        friendly_name: Nerdroom HDMI Switch
        host: !secret hdmi_switch_host
        sources:
          HDMI 1: NES
          HDMI 2: SENES
          HDMI 3: Nintendo N64
          HDMI 4: Wii U
          HDMI 5: HDMI 5
          HDMI 6: Xbox One
          HDMI 7: HDMI 7
          HDMI 8: Sega Genesis
          HDMI 9: Atari 2600+
          HDMI 10: HDMI 10
          HDMI 11: HDMI 11
          HDMI 12: HDMI 12
    #      HDMI 13: HDMI 13
    #      HDMI 14: HDMI 14
    #      HDMI 15: HDMI 15
    #      HDMI 16: HDMI 16

```
Example secrets.yaml file:
```yaml
# Use this file to store secrets like usernames and passwords.
# Learn more at https://www.home-assistant.io/docs/configuration/secrets/
upstairs_hdmi_switch_host: "192.168.1.10"
```

## Todo

1. Proper integration with config_flow

## License

This project is licensed under MIT license. See [LICENSE](LICENSE) file for details.
