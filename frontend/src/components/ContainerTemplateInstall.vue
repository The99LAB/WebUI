<template>
  <q-dialog v-model="dialogShown" full-width full-height>
    <q-layout
      view="hHh lpR fFf"
      container
      :class="{ 'bg-dark': $q.dark.isActive, 'bg-white': !$q.dark.isActive }"
    >
      <q-header bordered elevated>
        <q-toolbar>
          <q-toolbar-title v-if="dialogMode.startsWith('new')"
            >Create container</q-toolbar-title
          >
          <q-toolbar-title v-else-if="dialogMode.startsWith('edit')"
            >Edit container</q-toolbar-title
          >
          <q-btn
            icon="close"
            flat
            round
            dense
            v-close-popup
            @click="tab = 'general'"
          />
        </q-toolbar>
        <q-separator color="transparent" />
      </q-header>
      <q-page-container>
        <q-page padding>
          <div class="row" v-if="dialogMode == 'new'">
            <q-img
              :src="`data:image/png;base64,${dialogData.image}`"
              spinner-color="primary"
              class="dialog-img q-mr-md"
            />
            <div class="col q-ml-md">
              <div class="text-h6">{{ templateName }}</div>
              <div class="text-subtitle2">
                Maintainer: {{ dialogData.maintainer }}
              </div>
              <p>{{ dialogData.description }}</p>
            </div>
          </div>
          <q-separator
            spaced="lg"
            inset
            color="transparent"
            v-if="dialogMode == 'new'"
          />
          <q-form @submit="templateSubmit" ref="form">
            <p class="text-h6 q-mb-none">General</p>
            <q-input
              v-model="dialogData.config.repository"
              type="text"
              label="Repository"
              :readonly="dialogMode != 'new-custom'"
              :rules="[
                (val) => !!val || 'Field is required',
                (val) => !/\s/.test(val) || 'Field cannot contain whitespace',
              ]"
            />
            <q-input
              v-model="dialogData.config.tag"
              type="text"
              label="Repository Tag"
              :readonly="dialogMode != 'new-custom'"
              :rules="[
                (val) => !!val || 'Field is required',
                (val) => !/\s/.test(val) || 'Field cannot contain whitespace',
              ]"
            />
            <q-input
              v-model="dialogData.name"
              type="text"
              label="Name"
              :rules="[
                (val) => !!val || 'Field is required',
                (val) => !/\s/.test(val) || 'Field cannot contain whitespace',
              ]"
            />
            <q-select
              v-model="networkSelected"
              :options="networkOptions"
              label="Network"
              option-value="id"
            >
              <template v-slot:option="scope">
                <q-item v-bind="scope.itemProps">
                  <q-item-section>
                    <q-item-label>{{ scope.opt.name }}</q-item-label>
                    <q-item-label caption
                      >driver: {{ scope.opt.driver }}</q-item-label
                    >
                  </q-item-section>
                </q-item>
              </template>
              <template v-slot:selected-item="scope">
                <q-item v-bind="scope.itemProps" class="q-pl-none">
                  <q-item-section>
                    <q-item-label>{{ scope.opt.name }}</q-item-label>
                    <q-item-label caption
                      >driver: {{ scope.opt.driver }}</q-item-label
                    >
                  </q-item-section>
                </q-item>
              </template>
            </q-select>
            <q-checkbox
              v-model="networkFixedIp"
              label="Fixed IP"
              v-if="networkSelected.custom_ip"
            />
            <q-input
              v-model="networkIp"
              type="text"
              label="IP"
              v-if="networkSelected.custom_ip && networkFixedIp"
            >
              <template v-slot:append>
                <p class="text-body1">subnet: {{ networkSelected.subnet }}</p>
              </template>
            </q-input>
            <q-separator
              spaced="xl"
              v-if="dialogData.config.command.some((item) => item.editable)"
            />
            <p
              class="text-h6 q-mb-none"
              v-if="dialogData.config.command.some((item) => item.editable)"
            >
              Command
            </p>
            <div
              v-for="(command, index) in dialogData.config.command"
              :key="command.name"
            >
              <q-input
                v-model="command.value"
                type="text"
                :label="command.name"
                :hint="command.description"
                :rules="command.rules"
                lazy-rules="ondemand"
                v-if="command.editable"
              >
                <template
                  v-slot:append
                  v-if="
                    dialogMode == 'edit-custom' || dialogMode == 'new-custom'
                  "
                >
                  <q-btn
                    icon="mdi-delete"
                    flat
                    @click="removeField('command', index)"
                  />
                  <q-tooltip :offset="[0, 0]">Remove field</q-tooltip>
                </template>
              </q-input>
            </div>
            <q-separator
              spaced="xl"
              v-if="dialogData.config.env.some((item) => item.editable)"
            />
            <p
              class="text-h6 q-mb-none"
              v-if="dialogData.config.env.some((item) => item.editable)"
            >
              Environment
            </p>
            <div
              v-for="(item, index) in dialogData.config.env"
              :key="item.name"
            >
              <q-input
                v-model="item.value"
                :type="
                  item.type == 'int'
                    ? 'number'
                    : item.type == 'str'
                    ? 'text'
                    : 'text'
                "
                :label="item.name"
                :hint="item.description"
                :rules="item.rules"
                lazy-rules="ondemand"
                v-if="item.editable"
              >
                <template
                  v-slot:append
                  v-if="
                    dialogMode == 'edit-custom' || dialogMode == 'new-custom'
                  "
                >
                  <q-btn
                    icon="mdi-delete"
                    flat
                    @click="removeField('env', index)"
                  />
                  <q-tooltip :offset="[0, 0]">Remove field</q-tooltip>
                </template>
              </q-input>
            </div>
            <q-separator
              spaced="xl"
              v-if="dialogData.config.volumes.some((item) => item.editable)"
            />
            <p
              class="text-h6 q-mb-none"
              v-if="dialogData.config.volumes.some((item) => item.editable)"
            >
              Volumes
            </p>
            <div
              v-for="(item, index) in dialogData.config.volumes"
              :key="item.name"
            >
              <q-input
                v-model="item.value"
                type="text"
                :label="item.bind"
                :hint="item.description"
                v-if="item.editable"
              >
                <template v-slot:counter>
                  <p>mode: {{ item.mode }}</p>
                </template>
                <template
                  v-slot:append
                  v-if="
                    dialogMode == 'edit-custom' || dialogMode == 'new-custom'
                  "
                >
                  <q-btn
                    icon="mdi-delete"
                    flat
                    @click="removeField('volume', index)"
                  />
                  <q-tooltip :offset="[0, 0]">Remove field</q-tooltip>
                </template>
              </q-input>
            </div>
            <q-separator
              spaced="xl"
              v-if="
                networkSelected.driver == 'bridge' &&
                dialogData.config.ports.length > 0
              "
            />
            <p
              class="text-h6 q-mb-none"
              v-if="
                networkSelected.driver == 'bridge' &&
                dialogData.config.ports.length > 0
              "
            >
              Ports
            </p>
            <div
              v-for="(item, index) in dialogData.config.ports"
              :key="item.name"
            >
              <q-input
                v-model="item.value"
                type="number"
                :label="item.bind.toString()"
                :hint="item.description"
                v-if="networkSelected.driver == 'bridge'"
              >
                <template v-slot:counter>
                  <p>type: {{ item.type }}</p>
                </template>
                <template
                  v-slot:append
                  v-if="
                    dialogMode == 'edit-custom' || dialogMode == 'new-custom'
                  "
                >
                  <q-btn
                    icon="mdi-delete"
                    @click="removeField('port', index)"
                    flat
                  />
                  <q-tooltip :offset="[0, 0]">Remove field</q-tooltip>
                </template>
              </q-input>
            </div>
          </q-form>
        </q-page>
        <q-footer reveal bordered elevated>
          <q-toolbar>
            <q-btn
              flat
              label="Add custom field"
              v-if="dialogMode == 'edit-custom' || dialogMode == 'new-custom'"
              @click="customFieldDialogShow"
            />
            <q-space />
            <q-btn
              flat
              label="Reset"
              @click="() => $refs.form.resetValidation()"
            />
            <q-btn flat label="Submit" @click="$refs.form.submit()" />
          </q-toolbar>
        </q-footer>
      </q-page-container>
    </q-layout>
    <q-inner-loading :showing="dialogLoading" />
    <ErrorDialog ref="errorDialog" />
    <q-dialog v-model="customFieldDialog">
      <q-card style="width: 40em">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Add Custom Field</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-separator color="transparent" spaced="md" inset />
        <q-card-section>
          <q-form class="q-gutter-md" @submit="customFieldDialogSubmit">
            <q-select
              v-model="customFieldData.type"
              :options="customFieldData.typeOptions"
              label="Type"
              @update:model-value="(val) => customFieldDialogChangeType(val)"
            />
            <q-input
              v-model="customFieldData.name"
              type="text"
              label="Name"
              v-if="
                customFieldData.type == 'command' ||
                customFieldData.type == 'environment'
              "
            />
            <q-input
              v-model="customFieldData.description"
              type="text"
              label="Description"
            />
            <q-input
              v-model="customFieldData.value"
              type="text"
              label="Value"
              v-if="
                customFieldData.type == 'command' ||
                customFieldData.type == 'environment'
              "
            />
            <q-input
              v-model="customFieldData.hostpath"
              type="text"
              label="Host Path"
              v-if="customFieldData.type == 'volume'"
            />
            <q-input
              v-model="customFieldData.containerpath"
              type="text"
              label="Container Path"
              v-if="customFieldData.type == 'volume'"
            />
            <q-select
              v-model="customFieldData.volumemode"
              :options="customFieldData.volumeModeOptions"
              label="Volume Mode"
              v-if="customFieldData.type == 'volume'"
            />
            <q-input
              v-model="customFieldData.hostport"
              type="number"
              label="Host Port"
              v-if="customFieldData.type == 'port'"
            />
            <q-input
              v-model="customFieldData.containerport"
              type="number"
              label="Container Port"
              v-if="customFieldData.type == 'port'"
            />
            <q-select
              v-model="customFieldData.porttype"
              :options="customFieldData.portTypeOptions"
              label="Port Type"
              v-if="customFieldData.type == 'port'"
            />
            <p v-if="customFieldData.notes.length > 0" class="q-mb-none">
              Notes:
            </p>
            <p
              v-for="note in customFieldData.notes"
              :key="note"
              class="q-mt-none q-mb-none"
            >
              {{ note }}
            </p>
            <div class="row q-mt-lg">
              <q-space />
              <q-btn label="Submit" type="submit" color="primary" />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-dialog>
</template>

<script>
import ErrorDialog from "/src/components/ErrorDialog.vue";
export default {
  data() {
    return {
      dialogShown: false,
      dialogMode: null, // new, new-custom, edit, edit-custom
      dialogId: null,
      dialogLoading: false,
      dialogData: null,
      customFieldDialog: false,
      customFieldData: {
        typeOptions: ["command", "environment", "volume", "port"],
        portTypeOptions: ["tcp", "udp"],
        volumeModeOptions: ["rw", "ro"],
        type: null,
        name: null,
        description: null,
        value: null,
        hostpath: null,
        containerpath: null,
        volumemode: null,
        hostport: null,
        containerport: null,
        porttype: null,
        notes: [],
      },
      fieldRequired: [(val) => !!val || "Field is required"],
      networkOptions: [],
      networkSelected: [],
      networkFixedIp: false,
      networkIp: null,
      templateTitle: null,
    };
  },
  components: {
    ErrorDialog,
  },
  methods: {
    showDialog(id = null, mode) {
      this.dialogId = id;
      this.dialogMode = mode;
      if (this.dialogMode == "new-custom") {
        this.dialogData = {
          name: "Custom Container",
          config: {
            repository: "",
            tag: "",
            command: [],
            env: [],
            volumes: [],
            ports: [],
          },
        };
        this.dialogShown = true;
      } else {
        this.fetchTemplate();
      }
    },
    fetchNetworks() {
      this.$api
        .get("docker-manager/networks")
        .then((response) => {
          this.networkOptions = response.data;
          if (this.dialogMode.startsWith("new")) {
            // by default select the network with name 'host', if it doesn't exist, select the first network
            this.networkSelected = this.networkOptions.find(
              (item) => item.name == "host",
            );
            if (this.networkSelected == undefined) {
              this.networkSelected = this.networkOptions[0];
            }
          } else {
            this.networkSelected = this.networkOptions.find(
              (item) => item.name == this.dialogData.config.network.name,
            );
            this.networkFixedIp = this.dialogData.config.network.ip != null;
            this.networkIp = this.dialogData.config.network.ip;
          }
          this.dialogLoading = false;
        })
        .catch((error) => {
          let errormsg =
            error.response != undefined ? error.response.data : error;
          this.$refs.errorDialog.show("Error getting docker networks", [
            errormsg,
          ]);
        });
    },
    fetchTemplate() {
      this.dialogLoading = true;
      if (this.dialogMode == "new") {
        this.$api
          .get("/docker-manager/templates/" + this.dialogId)
          .then((response) => {
            this.dialogData = response.data;
            this.dialogData.config.env.forEach((item) => {
              this.generateRegexRules(item);
            });
            this.dialogData.config.command.forEach((item) => {
              this.generateRegexRules(item);
            });
            this.dialogShown = true;
            this.templateName = this.dialogData.name;
            this.dialogData.name = this.dialogData.name.replace(/\s/g, "-");
            this.fetchNetworks();
          })
          .catch((error) => {
            let errormsg =
              error.response != undefined ? error.response.data : error;
            this.$refs.errorDialog.show("Error loading template", [errormsg]);
          });
      } else if (this.dialogMode.startsWith("edit")) {
        this.$api
          .get("/docker-manager/container/" + this.dialogId)
          .then((response) => {
            this.dialogData = response.data;
            this.dialogData.config.env.forEach((item) => {
              this.generateRegexRules(item);
            });
            this.dialogData.config.command.forEach((item) => {
              this.generateRegexRules(item);
            });
            this.dialogShown = true;
            this.fetchNetworks();
          })
          .catch((error) => {
            let errormsg =
              error.response != undefined ? error.response.data : error;
            this.$refs.errorDialog.show("Error loading container", [errormsg]);
          });
      }
    },
    generateRegexRules(item) {
      // if regexrules item is not defined, set rules to empty array
      // if editable is false, set rules to empty array
      if (item.regexrules == undefined && item.editable == false) {
        item.rules = [];
        return;
      }
      if (item.regexrules == undefined && item.editable == true) {
        item.rules = this.fieldRequired;
      } else {
        item.rules = item.regexrules.map((rule) => {
          // convert regex string to regex object
          rule.regex = new RegExp(rule.regex);
          return (val) => rule.regex.test(val) || rule.message;
        });
      }
    },
    templateSubmit() {
      var data = JSON.parse(JSON.stringify(this.dialogData));
      // remove rules from data before submitting
      data.config.env.forEach((item) => {
        delete item.rules;
      });
      data.config.command.forEach((item) => {
        delete item.rules;
      });
      // set network data
      data.config.network = {
        name: this.networkSelected.name,
        ip:
          this.networkFixedIp && this.networkSelected.custom_ip
            ? this.networkIp
            : null,
      };
      if (this.dialogMode == "new") {
        // remove desctiption, maintainer, and image, id from data before submitting
        delete data.id;
        delete data.template_repository_id;
        delete data.description;
        delete data.maintainer;
        delete data.image;
        data.container_type = "template";
      } else if (this.dialogMode == "new-custom") {
        data.container_type = "custom";
      } else if (this.dialogMode.startsWith("edit")) {
        data.id = this.dialogId;
      }
      data.action = this.dialogMode == "new" ? "create" : "update";
      console.log("submit form data", data);
      this.dialogLoading = true;
      this.$api
        .post("/docker-manager/containers", data)
        .then((response) => {
          this.dialogLoading = false;
          this.dialogShown = false;
        })
        .catch((error) => {
          let errormsg =
            error.response != undefined ? error.response.data : error;
          this.$refs.errorDialog.show("Error submitting form", [errormsg]);
        });
    },
    customFieldDialogShow() {
      this.customFieldDialog = true;
      // if there is already a command in the config, remove the command option
      if (this.dialogData.config.command.length > 0) {
        this.customFieldData.typeOptions =
          this.customFieldData.typeOptions.filter((item) => item != "command");
      }
      this.customFieldData.type = this.customFieldData.typeOptions[0];
      this.customFieldDialogChangeType(this.customFieldData.type);
    },
    customFieldDialogChangeType(value) {
      this.customFieldData.notes = [];
      if (value == "command") {
        this.customFieldData.name = "Custom Command Name";
        this.customFieldData.description = "Custom Command Description";
        this.customFieldData.value = "custom-command --option";
        this.customFieldData.notes.push(
          "You can only add one custom command. If you want to execute multiple commands, you can use '&&' to separate them.'",
        );
      } else if (value == "environment") {
        this.customFieldData.name = "CUSTOM_ENV_VARIABLE";
        this.customFieldData.description =
          "Custom Environment Variable Description";
        this.customFieldData.value = "custom-value";
      } else if (value == "volume") {
        this.customFieldData.name = "Custom Volume Name";
        this.customFieldData.description = "Custom Volume Description";
        this.customFieldData.hostpath = "/host-path";
        this.customFieldData.containerpath = "/container-path";
        this.customFieldData.volumemode =
          this.customFieldData.volumeModeOptions[0];
      } else if (value == "port") {
        this.customFieldData.name = "Custom Port Name";
        this.customFieldData.description = "Custom Port Description";
        this.customFieldData.hostport = 8080;
        this.customFieldData.containerport = 80;
        this.customFieldData.porttype = this.customFieldData.portTypeOptions[0];
      }
    },
    customFieldDialogSubmit() {
      let customField;
      if (this.customFieldData.type == "command") {
        customField = {
          name: this.customFieldData.name,
          description: this.customFieldData.description,
          value: this.customFieldData.value,
          editable: true,
        };
        this.dialogData.config.command.push(customField);
        this.dialogData.config.command.forEach((item) => {
          this.generateRegexRules(item);
        });
      } else if (this.customFieldData.type == "environment") {
        customField = {
          name: this.customFieldData.name,
          value: this.customFieldData.value,
          description: this.customFieldData.description,
          type: "str",
          editable: true,
        };
        this.dialogData.config.env.push(customField);
        this.dialogData.config.env.forEach((item) => {
          this.generateRegexRules(item);
        });
      } else if (this.customFieldData.type == "volume") {
        customField = {
          bind: this.customFieldData.containerpath,
          value: this.customFieldData.hostpath,
          mode: this.customFieldData.volumemode,
          description: this.customFieldData.description,
          editable: true,
        };
        this.dialogData.config.volumes.push(customField);
      } else if (this.customFieldData.type == "port") {
        customField = {
          bind: this.customFieldData.containerport,
          value: this.customFieldData.hostport,
          type: this.customFieldData.porttype,
          description: this.customFieldData.description,
          editable: true,
        };
        this.dialogData.config.ports.push(customField);
      }
      this.customFieldDialog = false;
    },
    removeField(type, index) {
      if (type == "port") {
        this.dialogData.config.ports.splice(index, 1);
      } else if (type == "command") {
        this.dialogData.config.command.splice(index, 1);
      } else if (type == "env") {
        this.dialogData.config.env.splice(index, 1);
      } else if (type == "volume") {
        this.dialogData.config.volumes.splice(index, 1);
      }
    },
  },
};
</script>
