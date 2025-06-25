/* eslint-disable react/require-default-props */
import {
  Text, Input, NumberInput, createListCollection,
} from '@chakra-ui/react';
import { Field } from '@/components/ui/field';
import { Switch } from '@/components/ui/switch';
import {
  SelectContent,
  SelectItem,
  SelectRoot,
  SelectTrigger,
  SelectValueText,
} from '@/components/ui/select';
import { settingStyles } from './setting-styles';

// Common Props Types
interface SelectFieldProps {
  label: string
  value: string[]
  onChange: (value: string[]) => void
  collection: ReturnType<typeof createListCollection<{ label: string; value: string }>>
  placeholder: string
}

interface NumberFieldProps {
  label: string
  value: number | string
  onChange: (value: string) => void
  min?: number
  max?: number
  step?: number
  allowMouseWheel?: boolean
}

interface SwitchFieldProps {
  label: string
  checked: boolean
  onChange: (checked: boolean) => void
}

interface InputFieldProps {
  label: string
  value: string
  onChange: (value: string) => void
  placeholder?: string
}

// Reusable Components
export function SelectField({
  label,
  value,
  onChange,
  collection,
  placeholder,
}: SelectFieldProps): JSX.Element {
  return (
    <Field
      {...settingStyles.general.field}
      label={<Text {...settingStyles.general.field.label}>{label}</Text>}
    >
      <SelectRoot
        {...settingStyles.general.select.root}
        collection={collection}
        value={value}
        onValueChange={(e) => onChange(e.value)}
      >
        <SelectTrigger {...settingStyles.general.select.trigger}>
          <SelectValueText placeholder={placeholder} />
        </SelectTrigger>
        <SelectContent>
          {collection.items.map((item) => (
            <SelectItem key={item.value} item={item}>
              {item.label}
            </SelectItem>
          ))}
        </SelectContent>
      </SelectRoot>
    </Field>
  );
}

export function NumberField({
  label,
  value,
  onChange,
  min,
  max,
  step,
  allowMouseWheel,
}: NumberFieldProps): JSX.Element {
  return (
    <Field
      {...settingStyles.common.field}
      label={<Text {...settingStyles.common.fieldLabel}>{label}</Text>}
    >
      <NumberInput.Root
        {...settingStyles.common.numberInput.root}
        value={value.toString()}
        onValueChange={(details) => onChange(details.value)}
        min={min}
        max={max}
        step={step}
        allowMouseWheel={allowMouseWheel}
      >
        <NumberInput.Input {...settingStyles.common.numberInput.input} />
        <NumberInput.Control>
          <NumberInput.IncrementTrigger />
          <NumberInput.DecrementTrigger />
        </NumberInput.Control>
      </NumberInput.Root>
    </Field>
  );
}

export function SwitchField({ label, checked, onChange }: SwitchFieldProps): JSX.Element {
  return (
    <Field
      {...settingStyles.common.field}
      label={<Text {...settingStyles.common.fieldLabel}>{label}</Text>}
    >
      <Switch
        {...settingStyles.common.switch}
        checked={checked}
        onCheckedChange={(details) => onChange(details.checked)}
      />
    </Field>
  );
}

export function InputField({
  label,
  value,
  onChange,
  placeholder,
}: InputFieldProps): JSX.Element {
  return (
    <Field
      {...settingStyles.general.field}
      label={<Text {...settingStyles.general.field.label}>{label}</Text>}
    >
      <Input
        {...settingStyles.general.input}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </Field>
  );
}
